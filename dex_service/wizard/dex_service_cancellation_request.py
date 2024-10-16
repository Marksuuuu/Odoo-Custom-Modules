# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class DexServiceCancellationRequest(models.TransientModel):
    _name = 'dex_service.cancellation.request'

    cancellation_rsn = fields.Text(string="Reason")

    def button_submit(self):
        active_id = self._context.get('active_id')
        active_model = self.env.context.get('active_model')
        requests_res = self.env[active_model].browse(active_id)

        if requests_res:
            vals = {
                'cancelled_by': self.env.user.id,
                'cancellation_reason': self.cancellation_rsn,
                'cancelled_date': fields.Datetime.now(),
                'status': 'cancelled',
                'is_cancelled': True
            }

            requests_res.write(vals)
