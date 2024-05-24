# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class DexCancellationReasonWizard(models.TransientModel):
    _name = 'dex.cancellation.reason.wizard'

    cancellation_rsn = fields.Char(string="Reason")

    def button_submit(self):
        active_id = self._context.get('active_id')
        active_model = self.env.context.get('active_model')
        requests_res = self.env[active_model].browse(active_id)

        if requests_res:
            vals = {
                'cancelled_by': self.env.user.id,
                'cancellation_reason': self.cancellation_rsn,
                'cancelled_date': fields.Datetime.now(),
                'approval_status': 'cancel',
                'approval_link': False,
                'state': 'cancel'
            }

            requests_res.write(vals)
