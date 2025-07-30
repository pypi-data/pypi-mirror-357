import csv
import os
import warnings
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Union,
)

import pandas as pd
from bclearer_core.constants.standard_constants import (
    UTF_8_ENCODING_NAME,
)
from bclearer_interop_services.b_dictionary_service.table_as_dictionary_service.table_as_dictionary_to_dataframe_converter import (
    convert_table_as_dictionary_to_dataframe,
)
from bclearer_interop_services.file_system_service.objects.folders import (
    Folders,
)


def export_table_as_dictionary_to_csv(
    output_path: Union[str, Path],
    table: Dict[str, List[Any]],
    encoding: str = UTF_8_ENCODING_NAME,
) -> None:
    """
    Export a dictionary representation of a table to a CSV file.

    Args:
        output_path: Path where to save the CSV file
        table: Dictionary with column names as keys and lists of values as values
        encoding: Encoding to use for the file (default: utf-8)

    Deprecated:
        This function is maintained for backward compatibility.
        Use DelimitedTextFacades.export_dictionary_to_csv() instead.
    """
    warnings.warn(
        "This function is deprecated. Use DelimitedTextFacades.export_dictionary_to_csv() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    _export_table_as_dictionary_to_csv(
        output_path=output_path,
        table=table,
        encoding=encoding,
    )


def _export_table_as_dictionary_to_csv(
    output_path: Union[str, Path],
    table: Dict[str, List[Any]],
    encoding: str = UTF_8_ENCODING_NAME,
) -> None:
    """Internal implementation of export_table_as_dictionary_to_csv."""
    # Convert to DataFrame
    dictionary_as_table = convert_table_as_dictionary_to_dataframe(
        table_as_dictionary=table,
    )

    # Create directory if it doesn't exist
    directory = os.path.dirname(
        output_path
    )
    if (
        directory
        and not os.path.exists(
            directory
        )
    ):
        os.makedirs(directory)

    # Write to CSV
    dictionary_as_table.to_csv(
        path_or_buf=output_path,
        sep=",",
        quotechar='"',
        index=False,
        quoting=csv.QUOTE_ALL,
        escapechar="\\",
        encoding=encoding,
    )
