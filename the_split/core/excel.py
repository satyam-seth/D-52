from typing import Any, List

from xlwt import Workbook, XFStyle, easyxf  # type: ignore


def get_excel(sheet_name: str, columns: List[str], data: List[Any]) -> Workbook:
    """Function create and return excel workbook"""
    # create workbook and add sheet
    workbook = Workbook(encoding="utf-8")
    workbook_sheet = workbook.add_sheet(sheet_name)

    # add columns
    header_style = easyxf("font: bold on")
    for col_num, column in enumerate(columns):
        workbook_sheet.write(0, col_num, column, header_style)

    # add rows
    data_style = XFStyle()
    for row_num, row in enumerate(data, start=1):
        for col_num, value in enumerate(row):
            workbook_sheet.write(row_num, col_num, value, data_style)

    return workbook
