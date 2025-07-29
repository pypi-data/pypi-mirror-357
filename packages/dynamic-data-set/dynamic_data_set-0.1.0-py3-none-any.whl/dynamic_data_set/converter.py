"""Data conversion utilities."""

from pathlib import Path
from typing import Optional

import pandas as pd
import typer


class DataConverter:
    """Handles conversion between CSV and Parquet formats."""

    def __init__(self):
        self.supported_formats = {'.csv', '.parquet'}

    def parse_mapping(self, mapping_str: str) -> dict:
        """
        Parse mapping string like "old1:new1,old2:new2" into a dictionary.
        
        Args:
            mapping_str: String containing mapping rules
            
        Returns:
            Dictionary with old -> new value mappings
        """
        mapping = {}
        for pair in mapping_str.split(","):
            if ":" in pair:
                key, value = pair.split(":", 1)
                mapping[key.strip()] = value.strip()
        return mapping

    def validate_input_file(self, input_path: str) -> Path:
        """
        Validate input file exists and has supported format.
        
        Args:
            input_path: Path to input file
            
        Returns:
            Validated Path object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported
        """
        path = Path(input_path).resolve()
        
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
            
        if path.suffix.lower() not in self.supported_formats:
            raise ValueError(
                f"Unsupported input file format: {path.suffix}. "
                f"Supported formats: {', '.join(self.supported_formats)}"
            )
            
        return path

    def create_output_path(self, input_path: Path, output_path: Optional[str]) -> Path:
        """
        Create output path based on input and desired output.
        
        Args:
            input_path: Path to input file
            output_path: Optional output path
            
        Returns:
            Path object for output file
        """
        if output_path:
            return Path(output_path).resolve()
            
        # Auto-generate output path
        if input_path.suffix.lower() == '.csv':
            return input_path.with_suffix('.parquet')
        else:  # .parquet
            return input_path.with_suffix('.csv')

    def ensure_output_directory(self, output_path: Path) -> None:
        """
        Ensure output directory exists.
        
        Args:
            output_path: Path to output file
        """
        output_dir = output_path.parent
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            typer.echo(f"Created output directory: {output_dir}")

    def convert_csv_to_parquet(
        self, 
        input_path: Path, 
        output_path: Path,
        map_column: Optional[str] = None,
        map_values: Optional[str] = None
    ) -> None:
        """
        Convert CSV file to Parquet format.
        
        Args:
            input_path: Path to CSV file
            output_path: Path for output Parquet file
            map_column: Column name to apply value mapping
            map_values: Mapping rules string
        """
        try:
            df = pd.read_csv(input_path)
            
            # Apply column mapping if specified
            if map_column and map_values:
                if map_column not in df.columns:
                    typer.echo(f"Warning: Column '{map_column}' not found in CSV. Skipping mapping.")
                else:
                    mapping_dict = self.parse_mapping(map_values)
                    df[map_column] = df[map_column].map(mapping_dict).fillna(df[map_column])
                    typer.echo(f"Applied mapping on column '{map_column}': {mapping_dict}")
            
            df.to_parquet(output_path)
            typer.echo(f"Successfully converted CSV {input_path} to Parquet {output_path}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to convert CSV to Parquet: {e}")

    def convert_parquet_to_csv(self, input_path: Path, output_path: Path) -> None:
        """
        Convert Parquet file to CSV format.
        
        Args:
            input_path: Path to Parquet file
            output_path: Path for output CSV file
        """
        try:
            df = pd.read_parquet(input_path)
            df.to_csv(output_path, index=False)
            typer.echo(f"Successfully converted Parquet {input_path} to CSV {output_path}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to convert Parquet to CSV: {e}")

    def convert(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        map_column: Optional[str] = None,
        map_values: Optional[str] = None
    ) -> None:
        """
        Convert between CSV and Parquet formats automatically.
        
        Args:
            input_path: Path to input file
            output_path: Optional path for output file
            map_column: Column name for value mapping (CSV input only)
            map_values: Mapping rules string (CSV input only)
        """
        # Validate input
        input_file = self.validate_input_file(input_path)
        output_file = self.create_output_path(input_file, output_path)
        
        # Ensure output directory exists
        self.ensure_output_directory(output_file)
        
        # Perform conversion based on input format
        if input_file.suffix.lower() == '.csv':
            self.convert_csv_to_parquet(input_file, output_file, map_column, map_values)
        else:  # .parquet
            if map_column or map_values:
                typer.echo("Warning: Column mapping options are ignored when converting from Parquet to CSV.")
            self.convert_parquet_to_csv(input_file, output_file)
