import datetime
import hashlib
import re
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import formataddr
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class Agreement(models.Model):
    _name = 'agreement'
    _description = 'Agreement for Assets'

    name = fields.Char(string='Control No.', copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), tracking=True)

    name_of_person = fields.Many2one('hr.employee', string='Name of Person')

    department_of_person = fields.Many2one(related='name_of_person.department_id')

    unit = fields.Many2one('asset', string='Asset')

    serial_number = fields.Char(related='unit.serial_num', string='Serial Number', store=True)

    charger_with_usb_cable = fields.Char(related='unit.charger_with_usb_cable',string='Charger with usb cable')

    is_have_postpaid_number = fields.Boolean(related='unit.is_have_postpaid_number',default=False, string='Is have Postpaid Number')

    other_peripherals = fields.Char(related='unit.other_peripherals',string='Other Peripherals')

    remarks = fields.Char(related='unit.remarks',string='Remarks')

    digital_signature = fields.Binary(string="Signature", stored=True)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('dex.asset.agreement.sequence') or '/'
        return super(Agreement, self).create(vals)

    def show_agreement(self):
        return {
            'name': _("Agreement"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'agreement.wizard',
            'view_id': self.env.ref('dex_asset_agreement.agreement_wizard_form').id,
            'target': 'new',
            'context': {
                'default_name_of_person': self.name_of_person.id,
                'default_department_of_person': self.department_of_person,
                'default_unit': self.unit.id,
                'default_serial_number': self.serial_number,
                'default_charger_with_usb_cable': self.charger_with_usb_cable,
                'default_is_have_postpaid_number': self.is_have_postpaid_number,
                'default_other_peripherals': self.other_peripherals,
                'default_remarks': self.remarks,
                'default_digital_signature': self.digital_signature,
            }}


