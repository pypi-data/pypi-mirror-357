# DelimitedTextFacades

The `DelimitedTextFacades` class is a unified interface for working with CSV files and other delimited text formats within the bclearer framework. It serves as a facade that brings together the functionality scattered across various modules in the delimited_text package.

## Overview

This facade was created to:

1. Provide a single, consistent interface for all delimited text operations
2. Simplify the API by organizing related functions into logical groupings
3. Follow the same pattern as the `ExcelFacades` class
4. Enable better code organization and maintainability

## Usage

### Basic Usage

```python
from bclearer_interop_services.delimited_text.delimited_text_facades import DelimitedTextFacades

# Create a facade instance with a file path to load it immediately
facade = DelimitedTextFacades("/path/to/your/file.csv")

# Or create without a file and load later
facade = DelimitedTextFacades()
facade.load_csv("/path/to/your/file.csv")

# Get the loaded DataFrame
df = facade.get_dataframe()

# Modify and save back
df['new_column'] = df['existing_column'] * 2
facade.set_dataframe(df)
facade.save_csv()
```

### Static Methods

Most functionality is also available through static methods:

```python
# Read all CSV files from a directory
dataframes = DelimitedTextFacades.read_csv_files_from_directory("/path/to/directory")

# Export a list to CSV
DelimitedTextFacades.export_list_to_csv("/path/to/output.csv", ["item1", "item2", "item3"])

# Analyze CSV files
summary = DelimitedTextFacades.summarize_csv("/path/to/your/file.csv")
directory_summary = DelimitedTextFacades.summarize_directory("/path/to/directory")
detailed = DelimitedTextFacades.detailed_summary("/path/to/your/file.csv")
```

## API Reference

### Constructor

- `__init__(file_path=None)`: Initialize the facade with an optional file path to load immediately

### CSV Reading Methods

- `load_csv(file_path, encoding=None, sep=",", custom_header=None)`: Load a CSV file into a pandas DataFrame
- `get_dataframe()`: Get the currently loaded DataFrame
- `read_csv_files_from_directory(directory_path)` (static): Read all CSV files from a directory and return a dictionary of DataFrames

### CSV Writing Methods

- `save_csv(file_path=None, encoding=None, index=False)`: Save the current DataFrame to a CSV file
- `write_dataframes_to_csv_files(dataframes, output_directory, encoding='utf-8', index=False)` (static): Write a dictionary of DataFrames to CSV files
- `export_list_to_csv(output_path, data, encoding='utf-8')` (static): Export a list of strings to a CSV file
- `export_dictionary_to_csv(output_path, data, encoding='utf-8')` (static): Export a dictionary representation of a table to a CSV file

### CSV Analysis Methods

- `summarize_csv(csv_file_path)` (static): Generate a summary of a CSV file
- `summarize_directory(directory_path, file_extension=".csv")` (static): Generate summaries for all CSV files in a directory
- `detailed_summary(csv_file_path)` (static): Generate a detailed summary of a CSV file including column statistics

### DataFrame Manipulation Methods

- `set_dataframe(dataframe)`: Set the current DataFrame

### Utility Methods

- `detect_encoding(file_path)` (static): Detect the encoding of a file
- `convert_to_files_object(file_path)` (static): Convert a path string or Path to a Files object
- `convert_to_folders_object(directory_path)` (static): Convert a path string or Path to a Folders object

## Backward Compatibility

All original functions in the delimited_text module have been preserved with deprecation warnings to guide users toward using the facade instead. These functions will continue to work but may be removed in future versions.

Example of a deprecated function:

```python
from bclearer_interop_services.delimited_text.utf_8_csv_reader import get_table_from_csv_with_header

# Will work but will show a deprecation warning
df = get_table_from_csv_with_header("/path/to/file.csv", "utf-8", ",")

# Recommended approach using the facade
df = DelimitedTextFacades.load_csv("/path/to/file.csv")
```

## Migration Guide

To migrate from direct function calls to the facade:

1. Replace individual function imports with the DelimitedTextFacades import
2. Use the appropriate method from the facade
3. Update function parameters as needed (see examples in API Reference)

## Examples

### Reading and Analyzing a CSV File

```python
from bclearer_interop_services.delimited_text.delimited_text_facades import DelimitedTextFacades

# Create a facade instance and load a CSV file
facade = DelimitedTextFacades("/path/to/your/file.csv")

# Get summary information
summary = DelimitedTextFacades.detailed_summary("/path/to/your/file.csv")
print(f"File has {summary['data_summary']['row_count']} rows and {summary['data_summary']['column_count']} columns")

# Work with the loaded DataFrame
df = facade.get_dataframe()
print(df.head())
```

### Processing Multiple CSV Files

```python
from bclearer_interop_services.delimited_text.delimited_text_facades import DelimitedTextFacades

# Get summary of all CSV files in a directory
directory_summary = DelimitedTextFacades.summarize_directory("/path/to/directory")
print(directory_summary)

# Load all CSV files from a directory
dataframes = DelimitedTextFacades.read_csv_files_from_directory("/path/to/directory")

# Process each DataFrame
for name, df in dataframes.items():
    # Perform operations
    df['calculated_column'] = df['some_column'] * 2

# Save the processed DataFrames
DelimitedTextFacades.write_dataframes_to_csv_files(dataframes, "/path/to/output_directory")
```
