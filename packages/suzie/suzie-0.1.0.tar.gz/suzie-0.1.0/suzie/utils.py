"""
Utility functions for handling audio transcription and processing using OpenAI's API.

This module provides functionality to transcribe audio files, manage session states
and handle page switching in Streamlit applications. It also includes constants for the
full prompt template used in generating structured meeting minute notes.
"""

from io import BytesIO
import os
import numpy as np
import subprocess
import json
from pathlib import Path
import logging
import pypickle
from LLMlight import LLMlight

try:
    import whisper
except:
    logging.info('pip install openai-whisper')

import streamlit as st
from openai import OpenAI
import tempfile


#%%
def load_llm_model(modelname='', retrieval_method='naive_RAG', verbose='info'):
    model = LLMlight(model=modelname,
                     retrieval_method=retrieval_method,
                     alpha=None,
                     endpoint=st.session_state['endpoint'],
                     verbose=verbose,
                     )
    return model

#%%
def switch_page_button(page: st.Page, text: str | None = None, button_type: str = 'secondary'):
    """
    Generate a button in the Streamlit app to switch to another page.

    Parameters
    ----------
    page : st.Page
        The identifier of the target page.
    text : str or None, optional
        The label displayed on the button. If None, defaults to "Volgende".
    """
    if st.button(text or "Volgende", type=button_type):
        st.switch_page(page)

@st.cache_data(persist=True)
def transcribe_local(audio_path, user_select):
    # Load model: Can be "tiny", "small", "medium", "large"
    model = whisper.load_model(user_select).to("cpu")  # Explicitly set CPU
    # Create transcript
    transcript = model.transcribe(audio_path)
    # Return
    return transcript


@st.cache_data(persist=True)
def transcribe_audio_from_path(audio_path) -> str:
    client = OpenAI(api_key=st.session_state.openai_api_key)

    with open(audio_path, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file)

    return transcription.text


@st.cache_data(persist=True)
def transcribe_audio_streamlit_object(audio_file: BytesIO) -> str:
    """
    Transcribe an audio file using the Whisper-1 model provided by OpenAI.

    Parameters
    ----------
    audio_file : BytesIO
        The audio file as buffer or UploadedFile to be transcribed.

    Returns
    -------
    str
        Text transcription of the audio file.
    """
    client = OpenAI(api_key=st.session_state.openai_api_key)

    transcription = client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )
    return transcription.text


def init_session_key(key: str, default_value: str | None = None, overwrite: bool = True):
    """
    Initialize a session state key with an optional default value.

    Parameters
    ----------
    key : str
        The key to be set in the session state.
    default_value : str or None, optional
        The default value for the key if it doesn't exist yet.
    """
    if (key not in st.session_state) or overwrite:
        st.session_state[key] = default_value

def init_session_keys(overwrite=False):
    """Initialize multiple session state keys with default values."""
    # Check for .streamlit/secrets.toml
    secrets_path = os.path.join(os.getcwd(), '.streamlit', 'secrets.toml')
    if not os.path.exists(secrets_path):
        # st.warning(".streamlit/secrets.toml not found. Some features may not work as expected. Please create this file to provide necessary secrets.")
        # Set a fallback for openai_api_key to avoid crash
        openai_key = None
    else:
        openai_key = st.secrets["openai"]["key"] if "openai" in st.secrets and "key" in st.secrets["openai"] else None

    temp_dir = os.path.join(tempfile.gettempdir(), "suzie")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    init_session_key("openai_api_key", default_value=openai_key, overwrite=False)
    init_session_key("endpoints", default_value=['http://localhost:1234/v1/chat/completions', 'http://localhost:11434/api/generate'], overwrite=False)
    # Take the first endpoint as default
    init_session_key("endpoint", default_value=st.session_state['endpoints'][0], overwrite=False)
    init_session_key("temp_dir", default_value=temp_dir, overwrite=False)
    init_session_key("model", default_value="gpt-4o-mini", overwrite=False)
    init_session_key("model_names", default_value=["gpt-4o-mini"], overwrite=False)
    init_session_key("model_type", default_value='turbo', overwrite=False)
    init_session_key("save_path", default_value=None, overwrite=False)

    init_session_key("instruction_name", default_value=None, overwrite=overwrite)
    init_session_key("instruction", default_value=None, overwrite=overwrite)
    init_session_key("instructions", default_value=load_user_prompts(), overwrite=overwrite)

    init_session_key("project_name", default_value='', overwrite=overwrite)
    init_session_key("project_path", default_value='', overwrite=overwrite)
    init_session_key("audio_filepath", default_value=None, overwrite=overwrite)
    init_session_key("audio", default_value=None, overwrite=overwrite)
    init_session_key("minute_notes", overwrite=overwrite)
    init_session_key("audio_recording", default_value={}, overwrite=overwrite)
    init_session_key("audio_order", default_value=[], overwrite=overwrite)
    init_session_key("audio_names", default_value=[], overwrite=overwrite)
    init_session_key("bitrate", default_value='24k', overwrite=overwrite)
    init_session_key("timings", default_value=[], overwrite=overwrite)
    init_session_key("timings_llm", default_value=[], overwrite=overwrite)

    init_session_key('query', overwrite=overwrite)
    init_session_key('system', overwrite=overwrite)
    init_session_key('context', overwrite=overwrite) # This is the transcript of the audio file


def write_audio_to_disk(audio, filepath):
    if filepath is not None:
        # Write the uploaded file to the temporary directory
        with open(filepath, "wb") as f:
            f.write(audio.getbuffer())


def file_to_bytesio(file_path):
    if file_path is not None and os.path.isfile(file_path):
        # Get file ext and file path
        _, ext = os.path.splitext(file_path)

        # Open the file and read it into a BytesIO object
        with open(file_path, 'rb') as file:
            bytes_io = file.read()

        # Create a BytesIO buffer with the file data
        if ext == '.wav':
            bytes_io = BytesIO(bytes_io)

        # Return
        return bytes_io


def create_audio_chunks(temp_dir, file_path, segment_time=1800, ext='m4a'):
    if not file_path:
        return None

    # Define output filename pattern for chunks
    output_pattern = os.path.join(temp_dir, "chunk_%03d.m4a")  # Example: chunk_000.m4a, chunk_001.m4a, ...

    # FFmpeg command to split audio into 30-minute chunks
    command = [
        'ffmpeg',
        '-i', file_path,  # Input file
        '-f', 'segment',         # Enable segmenting
        '-segment_time', str(segment_time), # Split into 30-minute chunks
        '-c', 'copy',            # Keep original codec
        '-reset_timestamps', '1',
        '-map', '0',             # Ensure all streams are copied
        output_pattern           # Output files (chunk_000.m4a, chunk_001.m4a, etc.)
    ]

    # Run FFmpeg
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Get all chunk file paths
    chunk_files = sorted(Path(temp_dir).glob("chunk_*.m4a"))

    # Convert to a list of file paths as strings
    chunk_file_paths = [str(chunk) for chunk in chunk_files]

    return chunk_file_paths

def combine_audio_files(audio_files, temp_dir, bitrate, ext='.m4a'):
    # Define the path for the uploaded audio file
    # output_file = os.path.join(temp_dir, f'audio_file_stacked_{bitrate}' + '.m4a')
    output_file = os.path.join(temp_dir, f'audio_file_stacked_{bitrate}' + ext)
    # file_txt = 'file_list.txt'
    file_txt = os.path.join(temp_dir, 'file_list.txt')
    if os.path.isfile(output_file):
        return output_file

    # Create a temporary text file to list the audio files
    with open(file_txt, 'w') as f:
        for file in audio_files:
            f.write(f"file '{file}'\n")

    # FFmpeg command to combine the files using the concat demuxer
    command = [
        'ffmpeg',
        '-f', 'concat',         # Use the concat demuxer
        '-safe', '0',           # Allow unsafe file paths (if necessary)
        '-i', file_txt,         # Input file list
        '-c', 'copy',           # Copy codecs (no re-encoding)
        output_file             # Output file
    ]

    # Run the FFmpeg command
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Clean up the temporary file list
    # os.remove('file_list.txt')
    return output_file


# @st.cache_data
def compress_audio(file_path, bitrate='16k'):
    #  https://github.com/openai/whisper/discussions/870
    if file_path is not None:
        # Check bitrate
        logging.info('Checking bitrate..')
        bitrate_int = bitrate_to_kbps(bitrate)
        curr_bitrate = get_bitrate(file_path)
        if (curr_bitrate-1000) <= curr_bitrate and (curr_bitrate+1000) >= curr_bitrate:
            logging.info(f'Current audio file has bitrate within user defined range: {curr_bitrate} <return>')
            return file_path

        # Command to compress the audio using FFmpeg
        filename_new = os.path.split(file_path)[1].split('.')[0] + '_compressed_' + f'{bitrate}' + '.' + os.path.split(file_path)[1].split('.')[1]
        output_file = os.path.join(os.path.split(file_path)[0], filename_new)

        print(f'Start compression audio to {bitrate}..')
        if not os.path.isfile(output_file):
            with st.spinner(f"Wait for it... compressing audio.. from {curr_bitrate} to {bitrate_int}"):
                command = [
                    'ffmpeg',
                    '-i', file_path,  # Input file
                    '-b:a', bitrate,   # Set bitrate (e.g., '16k')
                    # '-vn',             # Disable video processing
                    output_file        # Output file
                ]

                # Run the command
                subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # st.write(output_file)
                # st.write(os.path.getsize(output_file))
        return output_file


def get_bitrate(file_path):
    """
    Checks if the audio file has a bitrate higher than the target.

    Args:
        file_path (str): Path to the audio file.

    Returns:
        int: bitrate
    """
    try:
        command = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=bit_rate',
            '-of', 'json',
            file_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        info = json.loads(result.stdout)
        current_bitrate = int(info['streams'][0]['bit_rate'])

        return current_bitrate
    except Exception as e:
        print(f"Error checking bitrate: {e}")
        return None  # Assume compression is required if we can't determine bitrate


def convert_wav_to_m4a(wav_filepath, output_directory=None, bitrate='128k', overwrite=False):
    """Convert a WAV file to M4A format using ffmpeg.

    Args:
        wav_filepath (str): Path to the input .wav file.

    Returns:
        str: Path to the converted .m4a file.
    """
    if not os.path.isfile(wav_filepath):
        raise FileNotFoundError(f"File not found: {wav_filepath}")

    # Get file ext and file path
    _, ext = os.path.splitext(wav_filepath)

    # Convert wav
    if ext == '.wav':
        print('>convert_wav_to_m4a')
        # Set new output directory
        if output_directory is not None and os.path.exists(output_directory) and os.path.isdir(output_directory):
            _, filename = os.path.split(wav_filepath)
            # Create output filename with .m4a extension
            m4a_filepath = os.path.join(output_directory, os.path.basename(wav_filepath))
            m4a_filepath = os.path.splitext(m4a_filepath)[0] + ".m4a"
        else:
            # Create output filename with .m4a extension
            m4a_filepath = os.path.splitext(wav_filepath)[0] + ".m4a"

        if overwrite and os.path.isfile(m4a_filepath):
            os.remove(m4a_filepath)
        elif (not overwrite) and os.path.isfile(m4a_filepath):
            st.warning(f'File found on disk; it is already converted {m4a_filepath}')
            return None

        # Construct the ffmpeg command
        command = [
            "ffmpeg",
            "-i", wav_filepath,  # Input file
            "-c:a", "aac",       # Convert to AAC codec
            "-b:a", bitrate,      # Set audio bitrate (adjust if needed)
            "-movflags", "+faststart",  # Optimize for streaming
            m4a_filepath         # Output file
        ]

        # Run the ffmpeg command
        # subprocess.run(command, check=True)
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    else:
        m4a_filepath = wav_filepath

    return m4a_filepath

def bitrate_to_kbps(bitrate_str):
    """Convert bitrate like '16k' to integer in bits per second."""
    if bitrate_str.lower().endswith('k'):
        return int(bitrate_str[:-1]) * 1000
    return int(bitrate_str)


def list_subdirectories(dirname):
    if not dirname or not os.path.exists(dirname):
        return []

    subdirs = [name for name in os.listdir(dirname)
               if os.path.isdir(os.path.join(dirname, name))]
    return subdirs

def set_project_paths(project_name):
    st.session_state["project_name"] = project_name
    st.session_state["project_path"] = os.path.join(st.session_state['temp_dir'], '' if project_name is None else project_name)
    st.session_state["save_path"] = os.path.join(st.session_state['project_path'], 'session_states.pkl')
    if not os.path.exists(st.session_state["project_path"]):
        os.makedirs(st.session_state["project_path"])

def save_session(save_audio=True):
    if save_audio:
        filtered_states = {k: v for k, v in st.session_state.items() if k not in ('demo')}
        pypickle.save(st.session_state["save_path"], filtered_states, overwrite=True)
    else:
        filtered_states = {k: v for k, v in st.session_state.items() if k not in ('audio')}
        pypickle.save(st.session_state["save_path"], filtered_states, overwrite=True)
    st.success('✅ Completed and session is saved!')


#%%
@st.cache_data
def load_user_prompts(path="./suzie/user_prompts", getfiles=None):
    # getfiles='minute_notes.txt'
    # getfiles = ['minute_notes.txt', 'heisessie.txt']

    prompts = {}
    if getfiles is not None and isinstance(getfiles, str):
        getfiles = [getfiles]

    for filename in os.listdir(path):
        if filename.endswith(".txt"):
            if getfiles is not None and (not np.isin(filename, getfiles)):
                continue

            filepath = os.path.join(path, filename)
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            parts = {
                "system": "",
                "query": "",
                "instructions": ""
            }

            current_key = None
            for line in content.splitlines():
                line = line.strip()
                if line.endswith(":") and line[:-1] in parts:
                    current_key = line[:-1]
                    continue
                if current_key:
                    parts[current_key] += line + "\n"

            # Strip trailing whitespace and store
            name_without_ext = os.path.splitext(filename)[0]
            prompts[name_without_ext] = {k: v.strip() for k, v in parts.items()}

    return prompts

