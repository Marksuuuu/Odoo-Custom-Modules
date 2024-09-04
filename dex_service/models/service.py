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


class Service(models.Model):
    _name = 'service'
    _description = 'Dex Service'
    _order = 'id desc'
    

    name = fields.Char(string='Control No.', copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), tracking=True)

    service_line_ids = fields.One2many('service.line', 'service_id')
    
    sales_coordinator = fields.Many2one('hr.employee', string='Sales Coordinator')
    
    daily_sales_report_date = fields.Datetime(string='Daily Sales Report', default=fields.Datetime.now)


    partner_id = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)], required=True)
    

    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    city = fields.Char(related='partner_id.city')
    state_id = fields.Many2one(related='partner_id.state_id')
    zip = fields.Char(related='partner_id.zip')
    country_id = fields.Many2one(related='partner_id.country_id')
    user_id = fields.Many2one(related='partner_id.user_id')
    type = fields.Selection(related='partner_id.type')
    service_type = fields.Many2one('service.type', string='Service Type')
    
    transfer_to_partner_id = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)])
    transfer_to_street = fields.Char(related='transfer_to_partner_id.street')
    transfer_to_street2 = fields.Char(related='transfer_to_partner_id.street2')
    transfer_to_city = fields.Char(related='transfer_to_partner_id.city')
    transfer_to_state_id = fields.Many2one(related='transfer_to_partner_id.state_id')
    transfer_to_zip = fields.Char(related='transfer_to_partner_id.zip')
    transfer_to_country_id = fields.Many2one(related='transfer_to_partner_id.country_id')
    transfer_to_type = fields.Selection(related='transfer_to_partner_id.type')
    transfer_to_user_id = fields.Many2one(related='transfer_to_partner_id.user_id')

    what_type = fields.Selection(
        [('by_invoice', 'By Invoice'), ('by_warranty', 'By Warranty'), ('by_edp_code', 'By EDP-Code'),('by_edp_code_not_existing', 'By EDP-Code (Not Existing)')], default=False,
        string='Type')
    
    is_client_blocked = fields.Boolean(default=False)
    
    block_reason = fields.Char(string='Block Reason')
    
    is_tranfered = fields.Boolean(default=False)
    transfer_reason = fields.Char(string='Transfer Reason')
    
    def open_form_view(self):
        pass  

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('create.sequence.form.sequence.srf') or '/'
        
        return super(Service, self).create(vals)

    def action_client_search(self):
        action = self.with_context(bypass_partner_validation=True).client_search()
        return action
    
    def client_search(self):
        action = {
            'name': 'Client Search',
            'type': 'ir.actions.act_window',
            'res_model': 'client.search',
            'view_mode': 'form',
            'target': 'new',
            'domain': [],
            'context': { }
        }
        return action

    def by_invoice(self):
        request_type = 1
        action = self.create_ticket_by(request_type, 'By Invoice', what_type='by_invoice')
        return action

    def by_warranty(self):
        request_type = 2
        action = self.create_ticket_by(request_type, 'By Warranty', what_type='by_warranty')
        return action

    def by_edp_code(self):
        request_type = 3
        action = self.create_ticket_by(request_type, 'By EDP-Code', what_type='by_edp_code')
        return action
    
    def by_edp_code_not_existing(self):
        request_type = 4
        action = self.create_ticket_by(request_type, 'By EDP-Code (Not Existing)', what_type='by_edp_code_not_existing')
        return action
    
    def create_so(self):
        if self.is_client_blocked == True:
            raise UserError("Can't Proceed This Service Blocked.. Please Unblock First!.")
        else:
            action = {
                'name': 'Create SO',
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'form',
                'target': 'new',
                'domain': [],
                'context': {
                    'default_service_id': self.id,
                    'default_partner_id': self.partner_id.id,
                    'default_what_type': self.what_type,
    
                }
            }
            return action
    
    def block_client(self):
        action = {
            'name': 'Block Client?',
            'type': 'ir.actions.act_window',
            'res_model': 'block.reason',
            'view_mode': 'form',
            'target': 'new',
            'domain': [],
            'context': {
                'default_service_id': self.id,
            }
        }
        return action
    
    def unblock_client(self):
        _logger.info('Un Blocked')
        self.is_client_blocked = False
        self.block_reason = False

    def create_ticket_by(self, request_type, type, what_type):
        action = {
            'name': f'Create Ticket {type}',
            'type': 'ir.actions.act_window',
            'res_model': 'create.ticket.by',
            'view_mode': 'form',
            'target': 'new',
            'domain': [],
            'context': {
                'default_service_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_what_type': what_type,
                'default_request_type': request_type,

            }
        }
        return action
    
    def transfer_to(self):
        action = {
            'name': 'Transfer Client',
            'type': 'ir.actions.act_window',
            'res_model': 'transfer.to',
            'view_mode': 'form',
            'target': 'new',
            'domain': [],
            'context': {
                'default_service': self.id,
                'default_partner_id': self.partner_id.id,

            }
        }
        return action
        
            


    

class ServiceLine(models.Model):
    _name = 'service.line'
    _description = 'Dex Service Line'

    service_id = fields.Many2one('service', string='Service Id', ondelete='cascade')
    name = fields.Char(string='Control No.', copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), tracking=True)
    status = fields.Selection(
        [('open', 'Open'), ('cancelled', 'Cancelled'),('close', 'Close'), ('pending', 'Pending'), ('waiting', 'Waiting')], default='open',
        string='Type')

    invoice_id = fields.Many2one('account.move', string='Invoice ID')
    purchase_date = fields.Date(string='Purchase Date')
    with_warranty = fields.Boolean(default=False)
    warranty_number = fields.Many2one('warranty', string='Warranty #')
    serial_number = fields.Char(string='Serial #')
    item_description = fields.Char(string='Item Description')
    client_name = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)], store=True)

    service_type = fields.Many2one('service.type', string='Service Type', store=True)
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
    
    what_type = fields.Selection(
        [('by_invoice', 'By Invoice'), ('by_warranty', 'By Warranty'), ('by_edp_code', 'By EDP-Code'),('by_edp_code_not_existing', 'By EDP-Code (Not Existing)')], default=False,
        string='Type')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('create.service.request.sequence.srs') or '/'
        return super(ServiceLine, self).create(vals)
    
    def check_count_of_report_print_count(self):
        search_for_assign_request = self.env['assign.request'].search([('service_id', '=', self.id)])
        _logger.info('search_for_assign_request {}'.format(search_for_assign_request.report_print_count))
        _logger.info('search {}'.format(self.id))
        # total_count = 0  
        # for rec in self:
        #     total_count += rec.report_print_count  
        # return total_count
    
    
    def assign_workers(self):
        for record in self:
            record_id = record.id
            view_id = self.env.ref('dex_service.assign_request_dex_service_action').id
            action = {
                'name': 'Assign Workers',
                'type': 'ir.actions.act_window',
                'res_model': 'assign.request',
                'view_mode': 'tree,form',
                # 'view_id': view_id,
                'target': 'current',
                'domain': [('service_id', '=', record_id)],
                'context': {
                    'default_service_id': record_id,
                    'default_call_date': self.call_date,
                    'default_look_for': self.look_for,
                    'default_assign_request_line_ids': [(0, 0, {'partner_id': self.client_name.id, 'look_for': self.look_for})],
                    'default_assign_request_service_time_ids': [(0, 0, {'partner_id': self.client_name.id, 'parts_cost_actual': self.charge})],
                    'default_assign_request_other_details_ids': [(0, 0, {'partner_id': self.client_name.id})]

                }
            }
            return action
    
    

    def show_thread(self):
        for record in self:
            record_id = record.id
            action = {
                'name': 'Create Thread',
                'type': 'ir.actions.act_window',
                'res_model': 'service.line.thread',
                'view_mode': 'tree,form',
                'target': 'current',
                'domain': [('service_line_main_ids', '=', record_id)],
                'context': {
                    'default_service_line_main_ids': record_id,
                    'default_client_name': self.client_name.id,
                    'default_call_date': self.call_date,
                    # 'default_look_for': self.look_for


                }
            }
            return action

    def create_thread(self):
        for record in self:
            record_id = record.id
            # view_id = self.env.ref('dex_service.create_thread_wizard').id
            action = {
                'name': 'Create Thread',
                'type': 'ir.actions.act_window',
                'res_model': 'create.thread.wizard',
                # 'views': [(view_id, 'form')],
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_status': self.status,
                    'default_service_line_main_ids': record_id,
                    'default_client_name': self.client_name.id,
                    'default_invoice_id': self.invoice_id.id,
                    'default_purchase_date': self.purchase_date,
                    'default_item_description': self.item_description,
                    'default_service_type': self.service_type.id,
                    'default_call_date': self.call_date,
                    'default_look_for': self.look_for




                }
            }
            return action
        
        
