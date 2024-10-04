from odoo import models, fields, api
import base64
import pandas as pd
import logging

_logger = logging.getLogger(__name__)


class DexServiceTransferTo(models.TransientModel):
    _name = 'dex_service.transfer.to'
    
    service = fields.Many2one('service')
    partner_id = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)])

    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    city = fields.Char(related='partner_id.city')
    state_id = fields.Many2one(related='partner_id.state_id')
    zip = fields.Char(related='partner_id.zip')
    country_id = fields.Many2one(related='partner_id.country_id')

    type = fields.Selection(related='partner_id.type')
    user_id = fields.Many2one(related='partner_id.user_id')
    
    transfer_to_partner_id = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)])
    transfer_to_street = fields.Char(related='transfer_to_partner_id.street')
    transfer_to_street2 = fields.Char(related='transfer_to_partner_id.street2')
    transfer_to_city = fields.Char(related='transfer_to_partner_id.city')
    transfer_to_state_id = fields.Many2one(related='transfer_to_partner_id.state_id')
    transfer_to_zip = fields.Char(related='transfer_to_partner_id.zip')
    transfer_to_country_id = fields.Many2one(related='transfer_to_partner_id.country_id')
    transfer_to_type = fields.Selection(related='transfer_to_partner_id.type')
    transfer_to_user_id = fields.Many2one(related='transfer_to_partner_id.user_id')
    
    transfer_reason = fields.Char(string='Transfer Reason', required=True)


    def btn_save_changes(self):
        active_id = self._context.get('active_id')
        active_model = self.env.context.get('active_model')
        requests_res = self.env[active_model].browse(active_id)

        if requests_res:
            vals = {
                'is_tranfered': True,
                'transfer_to_partner_id': self.transfer_to_partner_id.id,
                'transfer_reason': self.transfer_reason,
            }
            requests_res.write(vals)