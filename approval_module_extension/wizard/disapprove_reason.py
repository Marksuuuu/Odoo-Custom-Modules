# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class DisapproveReasonWizard(models.TransientModel):
    _name = 'disapprove.reason.wizard'

    disapprove_rsn = fields.Char(string="Reason")

    def button_submit(self):
        active_id = self._context.get('active_id')
        purchase_id = self.env['purchase.order'].browse(active_id)
        vals = {
            'disapproval_reason': self.disapprove_rsn,
            'approval_status': 'disapprove',
            'state': 'disapprove'
        }

        purchase_id.write(vals)
