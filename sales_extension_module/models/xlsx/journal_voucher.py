from odoo import models


class JournalVoucher(models.AbstractModel):
    _name = 'report.sales_extension_module.journal_voucher'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        format2 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': False})
        sheet = workbook.add_worksheet('JOURNAL VOUCHER')

        sheet.write(0, 5, 'TEAM PACIFIC CORPORATION', format2)
        sheet.write(1, 5, "JOURNAL VOUCHER", format2)
        sheet.write(5, 0, lines.name if lines.name is not None else '', format2)

        sheet.write(8, 0, 'Reference', format2)

        sheet.write(8, 1, lines.ref if lines.ref is not None else '', format2)

        sheet.write(8, 8, 'Date', format2)
        sheet.write(8, 9, lines.date.strftime('%B/%d/%Y') if lines.name is not None else '', format2)

        sheet.write(9, 0, 'Journal', format2)

        sheet.write(9, 1,
                    lines.journal_id.name + '(' + lines.journal_id.code + ')' if lines.journal_id.name is not None and lines.journal_id.code is not None else '',
                    format2)

        sheet.write(16, 0, 'Asset Category', format2)
        sheet.write(16, 1, 'Account', format2)
        sheet.write(16, 2, 'Partner', format2)
        sheet.write(16, 3, 'Label', format2)
        sheet.write(16, 4, 'Analytic Account', format2)
        sheet.write(16, 6, 'Amount in Currency', format2)
        sheet.write(16, 7, 'Currency', format2)
        sheet.write(16, 8, 'Debit', format2)
        sheet.write(16, 9, 'Credit', format2)




        count_row = 18  # Starting row
        code_count = 0  # Initialize a counter for non-empty x.account_id.code values

        for x in lines.line_ids:
            if not x.account_id:
                sheet.write(count_row, 1, ' ', format2)
                count_row += 1
            else:
                if x.account_id.code:  # Check if x.account_id.code is not empty
                    sheet.write(count_row, 1, x.account_id.code + ' ' + x.account_id.name, format2)
                    code_count += 1  # Increment the counter
                count_row += 1

        count_row = 18  # Starting row
        for x in lines.line_ids:
            if not x.asset_category_id:
                sheet.write(count_row, 0, ' ', format2)
                count_row += 1
            else:
                sheet.write(count_row, 0, x.asset_category_id.name, format2)
                count_row += 1

        count_row = 18  # Starting row
        for x in lines.line_ids:
            if not x.partner_id:
                sheet.write(count_row, 2, '', format2)  # Write an empty string
            else:
                sheet.write(count_row, 2, x.partner_id.name, format2)
            count_row += 1

        count_row = 18  # Starting row
        for x in lines.line_ids:
            if not x.name:
                sheet.write(count_row, 3, '', format2)  # Write an empty string
            else:
                sheet.write(count_row, 3, x.name, format2)
            count_row += 1

        count_row = 18  # Starting row
        for x in lines.line_ids:
            if not x.analytic_tag_ids:
                sheet.write(count_row, 4, '', format2)  # Write an empty string
            else:
                sheet.write(count_row, 4, x.analytic_tag_ids.name, format2)
            count_row += 1


        count_row = 18  # Starting row
        for x in lines.line_ids:
            if not x.currency_id:
                sheet.write(count_row, 7, '', format2)  # Write an empty string
            else:
                sheet.write(count_row, 7, x.currency_id.name, format2)
            count_row += 1

        count_row = 18  # Starting row
        for x in lines.line_ids:
            if not x.debit:
                sheet.write(count_row, 8, '', format2)  # Write an empty string
            else:
                sheet.write(count_row, 8, "{:,}".format(x.debit), format2)
            count_row += 1

        count_row = 18  # Starting row
        for x in lines.line_ids:
            if not x.credit:
                sheet.write(count_row, 9, '', format2)  # Write an empty string
            else:
                sheet.write(count_row, 9, "{:,}".format(x.credit), format2)
            count_row += 1

        sheet.write(code_count + 20, 4, 'Reviewed by:', format2)
        sheet.write(code_count + 22, 4, '_____________', format2)
        sheet.write(code_count + 20, 9, 'Approved by:', format2)
        sheet.write(code_count + 22, 9, '_____________', format2)
        sheet.write(code_count + 20, 0, 'Posted by:', format2)
        sheet.write(code_count + 22, 0, '_____________', format2)
