"""Page containing intro text Suzie."""

from utils import switch_page_button
import streamlit as st

#%%
def run_main():
    welcome_text = """
    # **Welcome to Suzie**
    Your AI assistant for summarizing, transcribing and meeting support.
    
    ---
    
    ## **How does it work?**
    1. **Add your API end-point or enter your OpenAI API key**:
       This ensures secure and personalized use.
    
    2. **Upload an audio file**:  
       - Use existing recordings.
    
    3. **Automatic transcription**:  
       Whisper transcribes your audio quickly and accurately into text.
    
    4. **Smart summaries and insights**:  
       The language model analyzes the transcript and provides clear summaries and key action points.
    
    ---
    
    ## **Important: Be careful with sensitive data!**
    - **When using the OpenAI key, it may process your data**: Although Suzie does not store your information, the OpenAI API may process the input to generate transcripts and summaries.
    - **Avoid submitting sensitive or confidential information**, such as personal details, financial data, or other private content.
    
    ---
    
    ## **Why use Suzie?**
    - ✅ **Save time**: Let AI handle the heavy lifting.
    - ✅ **Clear notes**: Get instant summaries and action points with zero effort.
    - ✅ **User-friendly**: Simple and intuitive interface.
    - ✅ **Versatile**: Perfect for meetings, interviews, webinars, and more.
    
    ---
    
    ## **How do I get started?**
    1. Make sure you have an OpenAI API key.
    2. Launch the app and follow the on-screen steps.
    3. Upload an audio file or start a live session — and let Suzie do the rest!
    
    ---
    
    ### **Enjoy using Suzie!**
    Have questions, feedback, or ideas? Let us know — together we’ll make note-taking even smarter and more efficient.
    """

    
    st.markdown(welcome_text)
    navigation()

#%%
def navigation():
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            switch_page_button("app_pages/audio_recording.py", text='Next Step: Upload/ Record Audio', button_type='primary')

# %%
run_main()
