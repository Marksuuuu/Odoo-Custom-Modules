from odoo import models, fields, api
import base64
import pandas as pd
import logging
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


    
class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def name_get(self):
        if self.env.context.get('for_invoice_select'):
            _logger.info(f"Name get called for: {self.ids}")
            return [
                (line.id, f'{line.name} -- {line.invoice_prefix}-{line.invoice_number}')
                for line in self
            ]
        return super().name_get()
    
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        if self.env.context.get('for_invoice_select'):
            if not args:
                args = []
            account_move = self.env['account.move'].search(args + ['|', '|', ('invoice_prefix', operator, name), ('name', operator, name), ('invoice_number', operator, name)], limit=limit)
            if account_move:
                return models.lazy_name_get(self.browse(account_move.ids))
            else:
                return []
        return super()._name_search(name, args, operator, limit, name_get_uid)