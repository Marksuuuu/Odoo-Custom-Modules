import datetime
import hashlib
import re
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import formataddr


class VehicleType(models.Model):
    _name = 'vehicle.type'
    _rec_name = 'vehicle_type'

    vehicle_type = fields.Char(string='Vehicle Name')
    vehicle_rate = fields.Float(string='Vehicle Rate')
