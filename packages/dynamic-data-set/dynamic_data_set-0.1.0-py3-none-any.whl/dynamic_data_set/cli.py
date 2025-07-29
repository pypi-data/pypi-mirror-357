"""Command-line interface for Dynamic Data Set."""

from typing import Optional

import typer

from . import __version__
from .converter import DataConverter
from .formatter import DataFormatter


app = typer.Typer(
    name="dynamic-data-set",
    help="A tool to convert CSV to Parquet and vice versa, and format file outputs.",
    add_completion=False,
)


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        typer.echo(f"Dynamic Data Set v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
):
    """Dynamic Data Set - CSV/Parquet conversion and formatting tool."""
    pass


@app.command(
    "convert",
    help="Convert CSV to Parquet or Parquet to CSV automatically based on input file extension."
)
def convert(
    input_file: str = typer.Option(
        ...,
        "--input",
        "-i",
        help="Path to the input CSV or Parquet file."
    ),
    output_file: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to the output file. Defaults to the input file directory with appropriate extension."
    ),
    map_column: Optional[str] = typer.Option(
        None,
        "--map-column",
        "-c",
        help="Column name to apply value mapping (only valid when input is CSV)."
    ),
    map_values: Optional[str] = typer.Option(
        None,
        "--map-values",
        "-m",
        help='Mapping rules in the format "old1:new1,old2:new2" (only valid when input is CSV).'
    )
):
    """Convert between CSV and Parquet formats."""
    try:
        converter = DataConverter()
        converter.convert(
            input_path=input_file,
            output_path=output_file,
            map_column=map_column,
            map_values=map_values
        )
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command(
    "format",
    help="Format and display the content of a CSV or Parquet file in a readable tabular form."
)
def format_file(
    file_path: str = typer.Argument(
        ...,
        help="Path to the CSV or Parquet file to format and display."
    ),
    max_rows: int = typer.Option(
        20,
        "--max-rows",
        "-n",
        help="Maximum number of rows to display."
    ),
):
    """Format and display file content."""
    try:
        formatter = DataFormatter()
        formatter.format_and_display(file_path, max_rows)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
