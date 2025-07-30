# bclearer-interop-services

A set of I/O and interop connectors for the bclearer framework. It provides adapters to read and write data between in-memory “universe” representations and a variety of storage, file formats, and application services.

## Installation

```bash
pip install bclearer-interop-services
```

## Key Features

- **Dictionary Service**
  Convert data to and from generic Python dictionaries (e.g., mapping objects to table dictionaries).
- **DataFrame Service**
  Utilities for standardizing, filtering, merging, and converting Pandas (and PySpark) DataFrames.
- **Delimited Text**
  Read/write CSV and other delimited formats.
- **Excel Services**
  Import/export Excel (.xlsx) files.
- **JSON, XML, HDF5, Parquet**
  Native serializers and readers for common data formats.
- **Relational Database Services**
  Access MS Access, SQLite, and other RDBMS via SQL interfaces.
- **Document Store Services**
  MongoDB and JSON file store support.
- **Graph Services**
  Neo4j connector and network analysis utilities.
- **EA Interop Service**
  COM-based, SQL, and XML import/export for Enterprise Architect models.
- **Session & Orchestration**
  Helpers to manage connections, sessions, and orchestrate multi-step data flows.

## Basic Usage

Below is a simple example using the Dictionary and DataFrame services:

```python
from bclearer_interop_services.b_dictionary_service.table_as_dictionary_service import TableAsDictionaryFromCsvFileReader
from bclearer_interop_services.b_dictionary_service.table_as_dictionary_service import TableAsDictionaryToDataFrameConverter

# Read data from a CSV file into a table-as-dictionary
reader = TableAsDictionaryFromCsvFileReader()
table_dict = reader.read('data/example.csv')

# Convert the table-as-dictionary to a Pandas DataFrame
converter = TableAsDictionaryToDataFrameConverter()
df = converter.convert(table_dict)

# Standardize column names and filter rows using the DataFrame service
from bclearer_interop_services.dataframe_service.dataframe_helper import DataFrameHelper

helper = DataFrameHelper()
df = helper.standardize_column_names(df)
df_filtered = df[df['status'] == 'ACTIVE']
```

## Documentation

Full documentation and examples can be found in the [GitHub repository](https://github.com/OntoLedgy/ol_bclearer_pdk/tree/develop/libraries/interop_services).

## License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.
