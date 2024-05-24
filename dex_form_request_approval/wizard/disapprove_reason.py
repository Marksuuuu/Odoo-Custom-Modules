# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools import datetime


class DexDisapproveReasonWizard(models.TransientModel):
    _name = 'dex.disapprove.reason.wizard'

    disapprove_rsn = fields.Char(string="Reason")

    def button_submit(self):
        active_id = self._context.get('active_id')
        active_model = self.env.context.get('active_model')
        requests_res = self.env[active_model].browse(active_id)
        vals = {
            'disapproved_by': self.env.user.id,
            'disapproval_reason': self.disapprove_rsn,
            'disapproved_date': datetime.now(),
            'approval_status': 'disapprove',
            'approval_link': False,
            'state': 'disapprove'
        }

        requests_res.write(vals)
