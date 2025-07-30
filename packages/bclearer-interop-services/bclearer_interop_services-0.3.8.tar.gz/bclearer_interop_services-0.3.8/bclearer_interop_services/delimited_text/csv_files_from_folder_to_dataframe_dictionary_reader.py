import os
import warnings
from pathlib import Path
from typing import Dict, Union

import pandas as pd
from bclearer_interop_services.file_system_service.objects.folders import (
    Folders,
)


def read_csv_files_from_folder_to_dataframe_dictionary(
    folders: Union[Folders, str, Path],
    **kwargs
) -> Dict[str, pd.DataFrame]:
    """
    Read all CSV files from a folder and return a dictionary of dataframes.

    Args:
        folders: Folder object or path to the folder
        **kwargs: Additional parameters to be passed to pandas.read_csv

    Returns:
        Dictionary with filenames as keys and pandas DataFrames as values

    Deprecated:
        This function is maintained for backward compatibility.
        Use DelimitedTextFacades.read_csv_files_from_directory() instead.
    """
    warnings.warn(
        "This function is deprecated. Use DelimitedTextFacades.read_csv_files_from_directory() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Convert to folder path string if needed
    folder_path = (
        folders.absolute_path_string
        if isinstance(folders, Folders)
        else str(folders)
    )

    # Proceed with original implementation
    return _read_csv_files_from_folder_to_dataframe_dictionary(
        folder_path, **kwargs
    )


def _read_csv_files_from_folder_to_dataframe_dictionary(
    folder: str, **kwargs
) -> dict:
    dataframe_dictionary = dict()

    csv_files = (
        __get_all_csv_files_from_folder(
            folder,
        )
    )

    for csv_file in csv_files:
        dataframe_dictionary = (
            __add_dataframe(
                csv_file,
                folder,
                dataframe_dictionary,
                **kwargs
            )
        )

    return dataframe_dictionary


def __get_all_csv_files_from_folder(
    folder: str,
) -> list:
    csv_files = list()

    for file in os.listdir(folder):
        if file.endswith(".csv"):
            csv_files.append(file)
    return csv_files


def __add_dataframe(
    csv_file: str,
    folder_name: str,
    dataframe_dictionary: dict,
    **kwargs
) -> dict:
    dataframe_name = csv_file.replace(
        ".csv",
        "",
    )

    csv_path = os.path.join(
        folder_name,
        csv_file,
    )

    dataframe = pd.read_csv(
        filepath_or_buffer=csv_path,
        **kwargs
    )

    dataframe_dictionary.update(
        {dataframe_name: dataframe},
    )

    return dataframe_dictionary
