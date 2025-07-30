import csv

from configurations.constants import (
    UTF_8_ENCODING,
    WRITE_ACRONYM,
)

# TODO: move to intero_services


def export_list_of_strings_to_csv(
    output_file_path: str,
    list_of_strings: list,
    encoding: str = UTF_8_ENCODING,
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
