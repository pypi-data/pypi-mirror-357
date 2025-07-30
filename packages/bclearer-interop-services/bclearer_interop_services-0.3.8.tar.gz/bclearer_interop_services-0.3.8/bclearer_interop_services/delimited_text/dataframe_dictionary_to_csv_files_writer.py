import csv
import os
import warnings
from pathlib import Path
from typing import Dict, Union

import pandas as pd


def write_dataframe_dictionary_to_csv_files(
    dataframe_dictionary: Dict[
        str, pd.DataFrame
    ],
    csv_files_folder: Union[str, Path],
    encoding: str = "utf-8",
    index: bool = False,
):
    """
    Write a dictionary of DataFrames to CSV files in a specific folder.

    Args:
        dataframe_dictionary: Dictionary with keys as filenames and values as DataFrames
        csv_files_folder: Directory where to save CSV files
        encoding: File encoding to use (default utf-8)
        index: Whether to include DataFrame index in output (default False)

    Deprecated:
        This function is maintained for backward compatibility.
        Use DelimitedTextFacades.write_dataframes_to_csv_files() instead.
    """
    warnings.warn(
        "This function is deprecated. Use DelimitedTextFacades.write_dataframes_to_csv_files() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    _write_dataframe_dictionary_to_csv_files(
        dataframe_dictionary=dataframe_dictionary,
        csv_files_folder=csv_files_folder,
        encoding=encoding,
        index=index,
    )


def _write_dataframe_dictionary_to_csv_files(
    dataframe_dictionary: Dict[
        str, pd.DataFrame
    ],
    csv_files_folder: Union[str, Path],
    encoding: str = "utf-8",
    index: bool = False,
):
    """Internal implementation of write_dataframe_dictionary_to_csv_files."""
    # Create output directory if it doesn't exist
    folder_path = str(csv_files_folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for (
        dataframe_name,
        dataframe,
    ) in dataframe_dictionary.items():
        write_dataframe_to_csv_file(
            dataframe=dataframe,
            csv_file_name_and_path=os.path.join(
                folder_path,
                f"{dataframe_name}.csv",
            ),
            encoding=encoding,
            index=index,
        )


def write_dataframe_to_csv_file(
    dataframe: pd.DataFrame,
    csv_file_name_and_path: Union[
        str, Path
    ],
    encoding: str = "utf-8",
    index: bool = False,
):
    """
    Write a DataFrame to a CSV file.

    Args:
        dataframe: DataFrame to write
        csv_file_name_and_path: Output file path
        encoding: File encoding to use (default utf-8)
        index: Whether to include DataFrame index in output (default False)

    Deprecated:
        This function is maintained for backward compatibility.
        Use DelimitedTextFacades.save_csv() instead.
    """
    warnings.warn(
        "This function is deprecated. Use DelimitedTextFacades.save_csv() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    _write_dataframe_to_csv_file(
        dataframe=dataframe,
        csv_file_name_and_path=csv_file_name_and_path,
        encoding=encoding,
        index=index,
    )


def _write_dataframe_to_csv_file(
    dataframe: pd.DataFrame,
    csv_file_name_and_path: Union[
        str, Path
    ],
    encoding: str = "utf-8",
    index: bool = False,
):
    """Internal implementation of write_dataframe_to_csv_file."""
    # Create directory if it doesn't exist
    directory = os.path.dirname(
        csv_file_name_and_path
    )
    if (
        directory
        and not os.path.exists(
            directory
        )
    ):
        os.makedirs(directory)

    dataframe.to_csv(
        path_or_buf=csv_file_name_and_path,
        sep=",",
        quotechar='"',
        index=index,
        quoting=csv.QUOTE_ALL,
        escapechar="\\",
        encoding=encoding,
    )
