import os
import sys
from typing import Dict, Any

# Constants for dictionary keys
FUNCTION_KEY = 'function'
EXCEPTION_TYPE_KEY = 'exception_type'
FILE_KEY = 'file'
LINE_NUMBER_KEY = 'line_number'
MESSAGE_KEY = 'msg'


def get_exception_details(function_name: str, exception: Exception) -> Dict[str, Any]:
    """
    Extract detailed information about an exception.
    
    Args:
        function_name: Name of the function where an exception occurred
        exception: The exception object
        
    Returns:
        Dictionary containing exception details including function name,
        exception type, file name, line number and error message
    """
    exception_type, _, exception_traceback = sys.exc_info()
    return {
        FUNCTION_KEY: function_name,
        EXCEPTION_TYPE_KEY: str(exception_type),
        FILE_KEY: os.path.split(exception_traceback.tb_frame.f_code.co_filename)[1],
        LINE_NUMBER_KEY: exception_traceback.tb_lineno,
        MESSAGE_KEY: str(exception)
    }
