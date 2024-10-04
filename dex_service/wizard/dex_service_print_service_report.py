from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class DexServicePrintServiceReport(models.TransientModel):
    _name = 'dex_service.print.service.report'

    report_print_count = fields.Integer()

    def btn_save_changes(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')

        if active_id and active_model:
            requests_res = self.env[active_model].browse(active_id)

            if requests_res:
                self.report_print_count = (self.report_print_count or 0) + 1

                vals = {
                    'report_print_count': self.report_print_count,
                }
                requests_res.write(vals)
                return self.print_service_report()
        return False

    def print_service_report(self):
        report_action = self.env.ref('dex_service.service_odoo_report_id').report_action(self)
        return report_action
