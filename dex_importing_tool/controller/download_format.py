# custom_module/controllers/controllers.py
from odoo import http
from odoo.http import request
import io
import xlsxwriter


class XlsxGenerator(http.Controller):

    @http.route('/dex/import/download', type='http', auth='user')
    def generate_xlsx(self, **kw):
        # Generate XLSX file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # Add sample data
        data = [
            ['EDP', 'LENGTH (MM)', 'WIDTH (MM)', 'HEIGHT (MM)', 'THICKNESS (MM)'],
            ['19301-00009', 100, 100, 100, 100],
        ]

        # Write data to the worksheet
        for row_num, row_data in enumerate(data):
            for col_num, cell_data in enumerate(row_data):
                worksheet.write(row_num, col_num, cell_data)

        # Apply formatting (e.g., make the first row bold)
        bold_format = workbook.add_format({'bold': True})
        worksheet.set_row(0, None, bold_format)

        # Close the workbook
        workbook.close()

        output.seek(0)
        xlsx_data = output.read()

        # Return XLSX file as response
        response = request.make_response(
            xlsx_data,
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename=template_for_import.xlsx')
            ]
        )

        return response
