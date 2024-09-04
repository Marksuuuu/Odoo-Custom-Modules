from odoo import models, fields, api
import base64
import pandas as pd
import logging

_logger = logging.getLogger(__name__)


class BlockReason(models.TransientModel):
    _name = 'block.reason'
    
    service = fields.Many2one('service')
    block_reason = fields.Char(string='Block Reason')


    def btn_save_changes(self):
        active_id = self._context.get('active_id')
        active_model = self.env.context.get('active_model')
        requests_res = self.env[active_model].browse(active_id)

        if requests_res:
            vals = {
                'is_client_blocked': True,
                'block_reason': self.block_reason,
            }
            requests_res.write(vals)