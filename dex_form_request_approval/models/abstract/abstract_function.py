import hashlib
import re
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

# from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class AbstractFunction(models.AbstractModel):
    _name = 'abstract.function'
    _description = 'Custom Function Plugin for Abstract Models'

    @api.model
    def create_bill_function(self, datas):
        default_tnvf_ids = []
        default_line_ids = []
        for_domain_in_account = self.env['account.account'].search([('name', '=', 'Expenses'), ('internal_group', '=', 'expense')], limit=1)
        for line in datas['tnvf_lines']:
            default_line_ids.append((0, 0, {
                'label': line['label'],
                'tnvf_personnel': line['tnvf_personnel'],
                'tnvf_package': line['tnvf_package'],
                'tnvf_from': line['tnvf_from'],
                'account_id': for_domain_in_account.id,
                'tnvf_to': line['tnvf_to'],
                'tnvf_amount': line['tnvf_amount'],
                'tnvf_purpose': line['tnvf_purpose'],
            }))

        default_tnvf_ids.append((0, 0, {
            'cbwl_lines': default_line_ids
        }))

        return {
            'name': _('Create Bill'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': datas['model_name'],
            'view_id': self.env.ref(datas['xml_id']).id,
            'target': 'new',
            'context': {
                'default_tnvf_ids': self.name,
                'default_cbwl_lines': default_line_ids,
                # 'default_transport_vehicle_type': datas['vehicle_type'].id,
                # 'default_transport_vehicle_type_rate': datas['vehicle_type_rate'],
                'default_total_rate': datas['total_rate'],
                'default_cargo_type': datas['cargo_type'] if datas['cargo_type'] else '',
                'default_currency_id': datas['currency_id'].id,
                'default_requesters_id': datas['requesters_id'].id,
                'default_journal_id': datas['journal_id'].id,
                'default_state': datas['state'],
            }
        }
