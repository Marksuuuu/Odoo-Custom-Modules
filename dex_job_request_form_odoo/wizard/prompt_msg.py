from odoo import models, fields, api
import base64
import pandas as pd
import logging

_logger = logging.getLogger(__name__)


class PromptMsg(models.TransientModel):
    _name = 'prompt.msg'

    reason_to_change = fields.Char(string='Reason To Change')

    date_from_user = fields.Date(string='Date From', tracking=True)
    total_days_user = fields.Integer(string='Total Days', tracking=True)


    def btn_save_changes(self):
        active_id = self._context.get('active_id')
        active_model = self.env.context.get('active_model')
        requests_res = self.env[active_model].browse(active_id)

        if requests_res:
            vals = {
                'date_from_user': self.date_from_user,
                'total_days_user': self.total_days_user,
                'reason_to_change': self.reason_to_change
            }
            requests_res.write(vals)


