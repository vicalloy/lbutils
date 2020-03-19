import codecs
from datetime import datetime
from io import BytesIO

from django.http import HttpResponse

try:
    import xlsxwriter as xlwt
except ImportError:
    pass


__all__ = (
    'export_xlsx', 'xlsw_write_row', 'simple_export2xlsx',
)


def export_xlsx(wb, output, fn):
    """
    export as excel
    wb:
    output:
    fn: file name
    """
    wb.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.ms-excel")
    cd = codecs.encode('attachment;filename=%s' % fn, 'utf-8')
    response['Content-Disposition'] = cd
    return response


def xlsw_write_row(ws, row_idx, row, fmt=None):
    """
    ws:
    row_idx: row number
    row: a list, data to write
    fmt: format for cell
    """
    for col_idx in range(len(row)):
        ws.write(row_idx, col_idx, row[col_idx], fmt)
    row_idx += 1
    return row_idx


def simple_export2xlsx(filename, titles, qs, func_data):
    """
    export as excel
    filename: file name
    titles: title for this table
    qs: queryset to export
    func_data: a function to format object to list. ex: `lambda o: [o.pk, o.name]`
    """
    output = BytesIO()
    wb = xlwt.Workbook(output)
    ws = wb.add_worksheet(filename)
    header_fmt = wb.add_format()
    header_fmt.set_bg_color('#C4D89E')
    row_idx = 0
    row_idx = xlsw_write_row(ws, row_idx, titles, header_fmt)
    for o in qs:
        row_idx = xlsw_write_row(ws, row_idx, func_data(o))
    fn = '%s-%s.xlsx' % (filename, datetime.now())
    return export_xlsx(wb, output, fn)
