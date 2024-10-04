from datetime import date, datetime
import hashlib
import re
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import formataddr
import json
import random

import logging

_logger = logging.getLogger(__name__)


class DexServiceNoProdExist(models.Model):
    _name = 'dex_service.no.prod.exist'
    _order = 'id desc'
    _description = 'Dex Service Not Existing'
    
    internal_reference = fields.Char(string='Internal Reference')
    name = fields.Char(string='Name')
    sales_price = fields.Integer(string='Sales Price')
    qty_available = fields.Integer(string='Quantity On Hand')
    virtual_available = fields.Integer(string='Forcasted Quantity')
    uom_id = fields.Many2one('uom.uom',string='Unit of Measure')
