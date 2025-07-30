import os

import pandas as pd
from bclearer_interop_services.excel_services.excel_facades import (
    ExcelFacades,
)


def convert_folder_with_excel_files_to_csv(
    tables_folder_path,
):
    file_paths = [
        os.path.join(dp, f)
        for dp, dn, filenames in os.walk(
            tables_folder_path,
        )
        for f in filenames
        if os.path.splitext(f)[1]
        == ".XLSX"
    ]

    for file_path in file_paths:
        if file_path.endswith(".XLSX"):
            excel_file_facade = (
                ExcelFacades(
                    file_path=file_path,
                )
            )
            excel_file_facade.convert_to_csv()
        else:
            print(
                f"Found non excel file {file_path}",
            )
