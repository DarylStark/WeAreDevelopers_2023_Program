"""Exceptions for the WAD2023 library.

Contains the exceptions for the WAD23 library.
"""


class WAD23Exception(BaseException):
    """Base class for WAD23 exceptions."""


class HTMLNotDownloadedException(WAD23Exception):
    """Users tries to parse something that doesn't exists."""
