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


class ServiceLineThread(models.Model):
    _name = 'service.line.thread'
    _description = 'Dex Service Line'


    service_line_main_ids = fields.Many2one('service.line')
    thread_name = fields.Char('Thread', readonly=True, copy=False)

    status = fields.Selection(
        [('open', 'Open'), ('cancelled', 'Cancelled'),('close', 'Close'), ('pending', 'Pending'), ('waiting', 'Waiting')], default='open',
        string='Type')

    invoice_id = fields.Many2one('account.move', string='Invoice ID')
    purchase_date = fields.Date(string='Purchase Date')
    with_warranty = fields.Boolean(default=False)
    warranty_number = fields.Many2one('warranty', string='Warranty #')
    serial_number = fields.Char(string='Serial #')
    item_description = fields.Char(string='Item Description')
    client_name = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)])

    service_type = fields.Many2one('service.type', string='Service Type')
    complaints = fields.Char(string='Complaints')
    feedback_count = fields.Integer(string='Feedback Count')

    street = fields.Char(related='client_name.street')
    street2 = fields.Char(related='client_name.street2')
    city = fields.Char(related='client_name.city')
    state_id = fields.Many2one(related='client_name.state_id')
    zip = fields.Char(related='client_name.zip')
    country_id = fields.Many2one(related='client_name.country_id')
    user_id = fields.Many2one(related='client_name.user_id')

    call_date = fields.Datetime(string='Call Date')
    requested_by = fields.Char(string='Requested by')
    phone_number = fields.Integer(string='Phone #')
    look_for = fields.Char(string='Look For')
    charge = fields.Float(string='Charge')
    free_of_charge = fields.Boolean(string='Free of Charge?')

    tentative_schedule_date = fields.Date(string='Tentative Schedule Date')

    other_instructions = fields.Char(string='Other Instructions')

    pending_reason = fields.Char(string='Pending Reason')

    thread_count = fields.Integer(string='Thread Count')

    count_field = fields.Integer(default=30)

    @api.model
    def generate_thread_name(self):
        """Generate a custom ID with the format DD/MM/ID-NAME"""
        today = datetime.today()
        day = today.strftime('%d')
        month = today.strftime('%m')

        sequence_code = 'service.line.thread.seq'
        sequence_number = self.env['ir.sequence'].next_by_code(sequence_code) or '000'

        return f"{sequence_number}/{day}/{month}-({self.service_line_main_ids.name.upper()})"


    def assign_thread_name(self):
        """Assign a custom ID to the record."""
        for record in self:
            if not record.thread_name:  # Only assign if not already set
                record.thread_name = self.generate_thread_name()

    @api.model
    def create(self, vals):
        # Create the record first
        record = super(ServiceLineThread, self).create(vals)
        # Assign custom ID after creation
        record.assign_thread_name()
        return record


