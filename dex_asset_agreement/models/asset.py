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


class Asset(models.Model):
    _name = 'asset'
    _description = 'Assets'
    _rec_name = 'device_name'

    asset_control_number = fields.Char(string='Control No.', copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), tracking=True)

    device_name = fields.Char(string='Device Name')

    serial_num = fields.Char(string='Serial Num')

    charger_with_usb_cable = fields.Char(string='Is have Postpaid Number')

    is_have_postpaid_number = fields.Boolean(default=False, string='Charger with usb cable')

    other_peripherals = fields.Char(string='Other Peripherals')

    remarks = fields.Char(string='Remarks')




    @api.model
    def create(self, vals):
        if vals.get('asset_control_number', '/') == '/':
            vals['asset_control_number'] = self.env['ir.sequence'].next_by_code('dex.asset.sequence') or '/'
        return super(Asset, self).create(vals)


