import csv
import warnings

from bclearer_core.constants.standard_constants import (
    UTF_8_ENCODING_NAME,
    WRITE_ACRONYM,
)


def export_list_of_strings_to_csv(
    output_file_path: str,
    list_of_strings: list,
    encoding: str = UTF_8_ENCODING_NAME,
) -> None:
    """
    Export a list of strings to a CSV file.

    Args:
        output_file_path: Path to the output CSV file
        list_of_strings: List of strings to export
        encoding: File encoding to use

    Deprecated:
        This function is maintained for backward compatibility.
        Use DelimitedTextFacades.export_list_to_csv() instead.
    """
    warnings.warn(
        "This function is deprecated. Use DelimitedTextFacades.export_list_to_csv() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    _export_list_of_strings_to_csv(
        output_file_path=output_file_path,
        list_of_strings=list_of_strings,
        encoding=encoding,
    )


def _export_list_of_strings_to_csv(
    output_file_path: str,
    list_of_strings: list,
    encoding: str = UTF_8_ENCODING_NAME,
) -> None:
    with open(
        output_file_path,
        mode=WRITE_ACRONYM,
        newline="",
        encoding=encoding,
    ) as file:
        writer = csv.writer(file)

        for text in list_of_strings:
            writer.writerow([text])
