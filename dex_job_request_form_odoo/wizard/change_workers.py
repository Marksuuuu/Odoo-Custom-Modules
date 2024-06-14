from odoo import models, fields, api
import base64
import pandas as pd
import logging

_logger = logging.getLogger(__name__)


class ChangeWorkers(models.TransientModel):
    _name = 'change.workers'

    reason_to_change = fields.Char(string='Reason To Change')
    is_change = fields.Boolean(default=False)
    workers_assigned_when_changed = fields.Many2many('res.users', string='Reassign Workers')

    def btn_save_changes(self):
        active_id = self._context.get('active_id')
        active_model = self.env.context.get('active_model')
        requests_res = self.env[active_model].browse(active_id)

        if requests_res:
            vals = {
                'workers_assigned_when_changed': [(6, 0, self.workers_assigned_when_changed.ids)],
                'reason_to_change': 'N/A' if not self.reason_to_change else self.reason_to_change,
                'is_change': True,
            }
            requests_res.write(vals)

