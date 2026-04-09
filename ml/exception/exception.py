import logging
import sys


def error_message_detail(error: Exception, error_detail: sys) -> str:
    """
    Extracts detailed error information including file name, line number, and the error message.

    :param error: The exception that occurred.
    :type error: Exception
    :param error_detail: The sys module to access traceback details.
    :type error_detail: sys
    :return: A formatted error message string.
    :rtype: str
    """
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    error_message = f"Error occurred in python script: [{file_name}] at line number [{line_number}]: {str(error)}"

    logging.error(error_message)

    return error_message


class CallForecastException(Exception):
    """
    Custom exception class for handling errors.
    """

    def __init__(self, error_message: str, error_detail: sys):
        """
        Initializes the SmartPhonesException with a detailed error message.

        :param error_message: A string describing the error.
        :type error_message: str
        :param error_detail: The sys module to access traceback details.
        :type error_detail: sys
        """
        super().__init__(error_message)
        self.error_message = error_message_detail(error_message, error_detail)

    def __str__(self) -> str:
        """
        Returns the string representation of the error message.

        :return: The error message.
        :rtype: str
        """
        return self.error_message
