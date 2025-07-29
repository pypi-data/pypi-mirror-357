"""Dynamic Data Set - CSV/Parquet conversion and formatting tool."""

__version__ = "0.1.0"
__author__ = "wenruohan"
__description__ = "A tool to convert CSV to Parquet and vice versa, and format file outputs."

from .cli import app

__all__ = ["app"]
