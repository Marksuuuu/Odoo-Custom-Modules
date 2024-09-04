from odoo import models, fields, api
import base64
import pandas as pd
import logging

_logger = logging.getLogger(__name__)


class CreateThreadWizard(models.TransientModel):
    _name = 'create.thread.wizard'

    status = fields.Selection(
        [('open', 'Open'), ('cancelled', 'Cancelled'),('close', 'Close'), ('pending', 'Pending'), ('waiting', 'Waiting')], default='open',
        string='Type')

    service_line_main_ids = fields.Many2one('service.line')


    invoice_id = fields.Many2one('account.move', string='Invoice ID')
    purchase_date = fields.Date(string='Purchase Date')
    with_warranty = fields.Boolean(default=False)
    warranty_number = fields.Many2one('warranty',string='Warranty #')
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
    type = fields.Selection(related='client_name.type')


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

    def btn_save_changes(self):
        active_id = self._context.get('active_id')
        active_model = self.env.context.get('active_model')
        requests_res = self.env[active_model].browse(active_id)

        if requests_res:
            vals = {
                'partner_id': self.partner_id.id,
            }
            requests_res.write(vals)


    def create_thread(self):
        thread_vals = {
            'status': self.status,
            'service_line_main_ids': self.service_line_main_ids.id,
            'invoice_id': self.invoice_id.id,
            'purchase_date': self.purchase_date,
            'with_warranty': self.with_warranty,
            'warranty_number': self.warranty_number,
            'serial_number': self.serial_number,
            'item_description': self.item_description,
            'client_name': self.client_name.id,
            'service_type': self.service_type.id,
            'complaints': self.complaints,
            'feedback_count': self.feedback_count,
            'call_date': self.call_date,
            'requested_by': self.requested_by,
            'phone_number': self.phone_number,
            'look_for': self.look_for,
            'charge': self.charge,
            'free_of_charge': self.free_of_charge,
            'tentative_schedule_date': self.tentative_schedule_date,
            'other_instructions': self.other_instructions,
            'pending_reason': self.pending_reason,
            'thread_count': self.thread_count,
            'count_field': self.count_field,
        }
        self.env['service.line.thread'].create(thread_vals)
        return True
