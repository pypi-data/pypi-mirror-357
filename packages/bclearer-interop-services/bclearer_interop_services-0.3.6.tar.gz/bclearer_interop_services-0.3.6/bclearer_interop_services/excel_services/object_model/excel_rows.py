from bclearer_interop_services.excel_services.object_model.excel_objects import (
    ExcelObjects,
)
from openpyxl.worksheet.worksheet import (
    Worksheet as OpenpyxlWorksheet,
)


class ExcelRows(ExcelObjects):
    def __init__(
        self,
        sheet: OpenpyxlWorksheet,
        index: int,
    ):
        self.sheet = sheet
        self.index = index
