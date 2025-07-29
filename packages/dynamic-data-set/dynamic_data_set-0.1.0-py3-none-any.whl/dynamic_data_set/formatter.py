"""Data formatting utilities."""

from pathlib import Path

import pandas as pd
import typer


class DataFormatter:
    """Handles formatting and display of data files."""

    def __init__(self):
        self.supported_formats = {'.csv', '.parquet'}

    def validate_file(self, file_path: str) -> Path:
        """
        Validate file exists and has supported format.
        
        Args:
            file_path: Path to file
            
        Returns:
            Validated Path object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported
        """
        path = Path(file_path).resolve()
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
            
        if path.suffix.lower() not in self.supported_formats:
            raise ValueError(
                f"Unsupported file format: {path.suffix}. "
                f"Supported formats: {', '.join(self.supported_formats)}"
            )
            
        return path

    def load_dataframe(self, file_path: Path) -> pd.DataFrame:
        """
        Load data from file into DataFrame.
        
        Args:
            file_path: Path to data file
            
        Returns:
            Loaded DataFrame
            
        Raises:
            RuntimeError: If file cannot be loaded
        """
        try:
            if file_path.suffix.lower() == '.csv':
                return pd.read_csv(file_path)
            else:  # .parquet
                return pd.read_parquet(file_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load file {file_path}: {e}")

    def format_and_display(self, file_path: str, max_rows: int = 20) -> None:
        """
        Format and display file content.
        
        Args:
            file_path: Path to file to display
            max_rows: Maximum number of rows to display
        """
        # Validate file
        validated_path = self.validate_file(file_path)
        
        # Load data
        df = self.load_dataframe(validated_path)
        
        # Display basic info
        typer.echo(f"File: {validated_path}")
        typer.echo(f"Format: {validated_path.suffix.upper()}")
        typer.echo(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        typer.echo("-" * 50)
        
        # Display data
        display_df = df.head(max_rows)
        typer.echo(display_df.to_string(index=False))
        
        if len(df) > max_rows:
            typer.echo(f"\n... and {len(df) - max_rows} more rows")
            typer.echo("Use --max-rows to display more rows")
