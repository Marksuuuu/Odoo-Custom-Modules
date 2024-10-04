from odoo import models, fields, api
import base64
import pandas as pd
import logging
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


    
class DexServiceServiceLineThread(models.Model):
    _inherit = 'dex_service.service.line.thread'
    
    def name_get(self):
        if self.env.context.get('select_service_thread'):
            return [
                (line.id, f'{line.thread_name} / {line.client_name.name} -- {line.street}-{line.city}')
                for line in self
            ]
        return super().name_get()
    
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        if self.env.context.get('select_service_thread'):
            if not args:
                args = []
            account_move = self.env['dex_service.service.line.thread'].search(args + ['|', '|', ('client_name', operator, name), ('street', operator, name), ('city', operator, name)], limit=limit)
            if account_move:
                return models.lazy_name_get(self.browse(account_move.ids))
            else:
                return []
        return super()._name_search(name, args, operator, limit, name_get_uid)