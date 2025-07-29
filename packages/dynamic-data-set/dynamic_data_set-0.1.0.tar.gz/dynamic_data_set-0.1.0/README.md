# Dynamic Data Set

A powerful CLI tool for converting between CSV and Parquet formats and displaying formatted data content.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Bidirectional Conversion**: Convert CSV to Parquet and Parquet to CSV
- **Data Transformation**: Apply value mappings during CSV to Parquet conversion
- **Data Visualization**: Display formatted data content with customizable row limits
- **Automatic Format Detection**: Automatically determines conversion direction based on file extension
- **Smart Output Naming**: Generates appropriate output filenames when not specified
- **Error Handling**: Comprehensive error handling with informative messages

## Installation

### From PyPI (when published)

```bash
pip install dynamic-data-set
```

### From Source

```bash
git clone https://github.com/wenruohan/dynamic-data-set.git
cd dynamic-data-set
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/wenruohan/dynamic-data-set.git
cd dynamic-data-set
pip install -e ".[dev]"
```

## Usage

The tool provides two main commands: `convert` and `format`.

### Converting Files

#### CSV to Parquet

```bash
# Basic conversion
dynamic-data-set convert -i data.csv

# Specify output file
dynamic-data-set convert -i data.csv -o output.parquet

# Apply value mapping during conversion
dynamic-data-set convert -i data.csv -c status -m "active:1,inactive:0"
```

#### Parquet to CSV

```bash
# Basic conversion
dynamic-data-set convert -i data.parquet

# Specify output file
dynamic-data-set convert -i data.parquet -o output.csv
```

### Displaying File Content

```bash
# Display first 20 rows (default)
dynamic-data-set format data.csv

# Display first 50 rows
dynamic-data-set format data.parquet --max-rows 50
```

### Command Options

#### Convert Command

- `-i, --input`: Path to the input CSV or Parquet file (required)
- `-o, --output`: Path to the output file (optional, auto-generated if not specified)
- `-c, --map-column`: Column name to apply value mapping (CSV input only)
- `-m, --map-values`: Mapping rules in format "old1:new1,old2:new2" (CSV input only)

#### Format Command

- `file_path`: Path to the CSV or Parquet file to display (positional argument)
- `-n, --max-rows`: Maximum number of rows to display (default: 20)

### Short Alias

You can also use the short alias `dds`:

```bash
dds convert -i data.csv
dds format data.parquet -n 30
```

### Version Information

```bash
dynamic-data-set --version
```

## Examples

### Example 1: Basic CSV to Parquet Conversion

```bash
# Convert sales.csv to sales.parquet
dynamic-data-set convert -i sales.csv
```

### Example 2: Parquet to CSV with Custom Output

```bash
# Convert data.parquet to report.csv
dynamic-data-set convert -i data.parquet -o report.csv
```

### Example 3: CSV Conversion with Value Mapping

```bash
# Convert CSV and map status values
dynamic-data-set convert -i users.csv -c status -m "active:1,inactive:0,pending:2"
```

### Example 4: Display Data Content

```bash
# Show first 10 rows of data
dynamic-data-set format dataset.parquet --max-rows 10
```

## Supported Formats

- **CSV**: Comma-separated values files
- **Parquet**: Apache Parquet columnar storage format

## Requirements

- Python 3.10 or higher
- pandas >= 2.0.0
- typer >= 0.9.0

## Development

### Setting up Development Environment

```bash
git clone https://github.com/wenruohan/dynamic-data-set.git
cd dynamic-data-set
uv sync
pre-commit install
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting && Check

```bash
uvx ruff@latest check --fix
```

### Pre-commit Integration

Ruff is integrated into the pre-commit hooks. To install the hooks:

```bash
pre-commit install
```

The hooks will automatically run Ruff checks before committing changes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0 (2025-06-23)

- Initial release
- CSV to Parquet conversion
- Parquet to CSV conversion
- Data formatting and display
- Value mapping during conversion
- Comprehensive CLI interface