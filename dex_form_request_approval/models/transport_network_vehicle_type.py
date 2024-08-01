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


class TransportNetworkVehicleType(models.Model):
    _name = 'transport.network.vehicle.type'
    _rec_name = 'tnv_type'

    tnv_type = fields.Char(string='Transport Network Name')
