import logging

__author__ = 'Erdogan Tasksen'
__email__ = 'erdogant@gmail.com'
__version__ = '0.1.0'

# Setup root logger
_logger = logging.getLogger('suzie')
_log_handler = logging.StreamHandler()
_fmt = '[{asctime}] [{name}] [{levelname}] {msg}'
_formatter = logging.Formatter(fmt=_fmt, style='{', datefmt='%d-%m-%Y %H:%M:%S')
_log_handler.setFormatter(_formatter)
_log_handler.setLevel(logging.DEBUG)
_logger.addHandler(_log_handler)
_logger.propagate = False


# module level doc-string
__doc__ = """
suzie
=====================================================================

suzie is for...

Example
-------
>>> import suzie as suzie
>>> model = suzie.fit_transform(X)
>>> fig,ax = suzie.plot(model)

References
----------
https://github.com/erdogant/suzie

"""
