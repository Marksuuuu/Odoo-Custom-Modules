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


class DexServiceServiceLineThread(models.Model):
    _name = 'dex_service.service.line.thread'
    _rec_name = 'thread_name'
    _order = 'id desc'
    _description = 'Dex Service Line'


    service_line_main_ids = fields.Many2one('service.line')
    thread_name = fields.Char('Thread', readonly=True, copy=False)

    status = fields.Selection(
        [('open', 'Open'), ('cancelled', 'Cancelled'),('close', 'Close'), ('pending', 'Pending'), ('waiting', 'Waiting')], default='open',
        string='Status')

    invoice_id = fields.Many2one('account.move', string='Invoice ID')
    purchase_date = fields.Date(string='Purchase Date')
    with_warranty = fields.Boolean(default=False)
    warranty_number = fields.Many2one('warranty', string='Warranty #')
    serial_number = fields.Char(string='Serial #')
    item_description = fields.Char(string='Item Description')
    client_name = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)])

    service_type = fields.Many2one('dex_service.service.type', string='Service Type')
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
    
    requesters_id = fields.Many2one('res.users', string='Requester', default=lambda self: self.env.user.id)
    
    is_scheduled = fields.Boolean(default=False)
    
    invoice_number = fields.Char(string='Invoice Number')
    
    trouble_reported = fields.Char(string='Trouble Reported')
    
    number_of_units = fields.Integer(string='Number of Units')
    
    brand_id = fields.Many2one('dex_brand_series.brand')

    edp_code = fields.Many2one(
        'product.template',
        string='EDP-Code',
        domain=[('default_code', '!=', False)]
    )
    
    def print_service_request_form(self):
        return self.env.ref('dex_service.service_request_form_report_id').render_qweb_pdf([self.id])[0]
    
    def print_acknowledgment_form(self):
        return self.env.ref('dex_service.acknowledgment_form_report_id').render_qweb_pdf([self.id])[0]
    
    def print_test(self):
        return self.env.ref('dex_service.acknowledgment_form_report_id').report_action(self)

    
    def print_report(self):
        return self.env.ref('dex_service.service_request_form_report_id').report_action(self)
    
    def set_close(self):
        self.status = 'close'
    

    @api.model
    def generate_thread_name(self):
        """Generate a custom ID with the format DD/MM/ID-NAME"""
        today = datetime.today()
        day = today.strftime('%d')
        month = today.strftime('%m')

        sequence_code = 'dex_service.service.line.thread.seq'
        sequence_number = self.env['ir.sequence'].next_by_code(sequence_code) or '000'

        return f"{sequence_number}/{day}/{month}-({self.service_line_main_ids.name.upper()})"


    def assign_thread_name(self):
        for record in self:
            if not record.thread_name:
                record.thread_name = self.generate_thread_name()

    @api.model
    def create(self, vals):
        record = super(DexServiceServiceLineThread, self).create(vals)
        record.assign_thread_name()
        return record


