import pytest
from seKM.Utilities import get_exception_details


def test_get_exception_details_with_valid_exception(mocker):
    """Test if get_exception_details correctly extracts details of an exception."""
    # Mock sys.exc_info to provide controlled traceback
    mock_tb = mocker.Mock()
    mock_tb.tb_frame.f_code.co_filename = "test_file.py"
    mock_tb.tb_lineno = 25
    mocker.patch("sys.exc_info", return_value=(ValueError, None, mock_tb))

    exception = ValueError("Test error message")
    result = get_exception_details("test_function", exception)
    print(result)
    assert result["function"] == "test_function"
    assert result["exception_type"] == str(ValueError)
    assert result["file"] == "test_file.py"
    assert result["line_number"] == 25
    assert result["msg"] == "Test error message"
