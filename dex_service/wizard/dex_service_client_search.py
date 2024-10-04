from odoo import models, fields, api
import base64
import pandas as pd
import logging

_logger = logging.getLogger(__name__)


class DexServiceClientSearch(models.TransientModel):
    _name = 'dex_service.client.search'

    partner_id = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)])

    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    city = fields.Char(related='partner_id.city')
    state_id = fields.Many2one(related='partner_id.state_id')
    zip = fields.Char(related='partner_id.zip')
    country_id = fields.Many2one(related='partner_id.country_id')

    type = fields.Selection(related='partner_id.type')
    user_id = fields.Many2one(related='partner_id.user_id')

    def btn_save_changes(self):
        active_id = self._context.get('active_id')
        active_model = self.env.context.get('active_model')
        requests_res = self.env[active_model].browse(active_id)

        if requests_res:
            vals = {
                'partner_id': self.partner_id.id,
            }
            requests_res.write(vals)
