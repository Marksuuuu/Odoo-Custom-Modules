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


class EmailSetup(models.Model):
    _name = 'email.setup'
    _rec_name = 'form_request_type'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    email_setup_lines = fields.One2many('email.setup.line', 'email_setup_ids')


    form_request_type = fields.Selection([
        ('official_business', 'Official Business Form'),
        ('it_request', 'IT Request Form'),
        ('overtime_authorization', 'Overtime Authorization'),
        ('gasoline_allowance', 'Gasoline Allowance'),
        ('online_purchases', 'Online Purchases'),
        ('cash_advance', 'Request for Cash Advance'),
        ('grab_request', 'Grab Request Form'),
        ('client_pickup', 'Client Pickup Permit'),
        ('payment_request', 'Payment Request'),
        ('job_request', 'Job Request')], string='Form Request Type', store=True, tracking=True, default='job_request')

class EmailSetupLine(models.Model):
    _name = 'email.setup.line'

    email_setup_ids = fields.Many2one('email.setup')

    requesters_id = fields.Many2one('hr.employee', string='Requesters', required=False, tracking=True)
    requesters_email = fields.Char(related='requesters_id.work_email', string='Requesters Email', tracking=True,
                                   store=True)


