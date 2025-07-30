import filecmp
import os
import sys
import warnings

import pandas
from bclearer_core.constants.standard_constants import (
    UTF_8_ENCODING_NAME,
)
from bclearer_interop_services.file_system_service.encoding.file_encoding_detector import (
    detect,
)
from bclearer_interop_services.file_system_service.objects.files import (
    Files,
)


def convert_utf_8_csv_with_header_file_to_dataframe(
    utf_8_csv_file: Files,
) -> pandas.DataFrame:
    """
    Convert a UTF-8 CSV file to a pandas DataFrame.

    Args:
        utf_8_csv_file: File object representing the CSV file

    Returns:
        pandas DataFrame containing the CSV data

    Deprecated:
        This function is maintained for backward compatibility.
        Use DelimitedTextFacades.load_csv() instead.
    """
    warnings.warn(
        "This function is deprecated. Use DelimitedTextFacades.load_csv() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    dataframe = _get_table_from_csv_with_header(
        relative_filename=utf_8_csv_file.absolute_path_string,
        file_encoding=UTF_8_ENCODING_NAME,
        sep=",",
    )

    return dataframe


def get_table_from_csv_with_header(
    relative_filename: str,
    file_encoding: str,
    sep: str,
    custom_header=None,
):
    """
    Read a CSV file with a header into a pandas DataFrame.

    Args:
        relative_filename: Path to the CSV file
        file_encoding: Encoding of the file
        sep: Separator character
        custom_header: Optional list of column names to use

    Returns:
        pandas DataFrame containing the CSV data

    Deprecated:
        This function is maintained for backward compatibility.
        Use DelimitedTextFacades.load_csv() instead.
    """
    warnings.warn(
        "This function is deprecated. Use DelimitedTextFacades.load_csv() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    return _get_table_from_csv_with_header(
        relative_filename=relative_filename,
        file_encoding=file_encoding,
        sep=sep,
        custom_header=custom_header,
    )


def _get_table_from_csv_with_header(
    relative_filename: str,
    file_encoding: str,
    sep: str,
    custom_header=None,
):
    read_options = {
        "dtype": object,
        "encoding": file_encoding,
        "keep_default_na": False,
        "na_values": [""],
        "sep": sep,
    }

    if custom_header is not None:
        read_options["names"] = (
            custom_header
        )
        read_options["header"] = (
            0 if custom_header else None
        )

    data_frame = pandas.read_csv(
        relative_filename,
        **read_options
    )

    return data_frame


def get_table_from_csv_with_header_with_encoding_detection(
    relative_filename: str,
    custom_header=None,
):
    """
    Read a CSV file with automatic encoding detection.

    Args:
        relative_filename: Path to the CSV file
        custom_header: Optional list of column names to use

    Returns:
        pandas DataFrame containing the CSV data

    Deprecated:
        This function is maintained for backward compatibility.
        Use DelimitedTextFacades.load_csv() instead.
    """
    warnings.warn(
        "This function is deprecated. Use DelimitedTextFacades.load_csv() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    return _get_table_from_csv_with_header_with_encoding_detection(
        relative_filename=relative_filename,
        custom_header=custom_header,
    )


def _get_table_from_csv_with_header_with_encoding_detection(
    relative_filename: str,
    custom_header=None,
):
    file_encoding = detect(
        relative_filename,
    )

    read_options = {
        "encoding": file_encoding,
    }

    if custom_header is not None:
        read_options["names"] = (
            custom_header
        )
        read_options["header"] = (
            0 if custom_header else None
        )

    data_frame = pandas.read_csv(
        relative_filename,
        **read_options
    )

    return data_frame


def __check_if_read_was_successful(
    dataframe: pandas.DataFrame,
    source_relative_filename: str,
    file_encoding: str,
    sep: str,
):
    read_file_relative_filename = source_relative_filename.replace(
        ".csv",
        "_read.csv",
    )

    dataframe.to_csv(
        path_or_buf=read_file_relative_filename,
        encoding=file_encoding,
        sep=sep,
        index=False,
    )

    filecmp.clear_cache()

    read_was_successful = filecmp.cmp(
        source_relative_filename,
        read_file_relative_filename,
        shallow=False,
    )

    if read_was_successful:
        os.remove(
            read_file_relative_filename,
        )

        return

    sys.exit(
        "Load was terminated because data was corrupted while reading from "
        + source_relative_filename,
    )
