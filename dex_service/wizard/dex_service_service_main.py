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


class DexServiceServiceMain(models.TransientModel):
    _name = 'dex_service.service.main'
    _description = 'Dex Service'
    _order = 'id desc'
    

    name = fields.Char(string='Control No.', copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), tracking=True)

    service_main_line_ids = fields.One2many('service.main.line', 'service_main_id')
    service_main_sale_order = fields.One2many('service.main.sale.order', 'service_main_id')
    
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
    service_type = fields.Many2one('dex_service.service.type', string='Service Type')
    
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
    
    amount_untaxed = fields.Integer(string='Untaxed Amount', readonly=True)
    amount_tax = fields.Integer(string='Taxes', readonly=True)
    amount_total = fields.Integer(string='Total', readonly=True)
    

    @api.model
    def find_or_create_record(self, search_criteria, default_values):
        record = self.env['service'].search(search_criteria)
        if not record:
            record = self.env['service'].create(default_values)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service',
            'res_model': 'service',
            'view_mode': 'form',
            'res_id': record.id,
            'view_id': False,
        }
    
    def action_find_or_create(self):
        search_criteria = [('partner_id', '=', self.partner_id.id)]
        default_values = {'partner_id': self.partner_id.id}
        return self.find_or_create_record(search_criteria, default_values)
            
    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            partner_id_data = self.env['service'].search([('partner_id', '=', self.partner_id.id)])
            sale_order_data = self.env['sale.order'].search([('partner_id', '=', self.partner_id.id)])
    
            self.service_main_line_ids = [(5, 0, 0)]
            self.service_main_sale_order = [(5, 0, 0)]
            self.amount_untaxed = 0
            self.amount_tax = 0
            self.amount_total = 0
    
            if not partner_id_data:
                _logger.info('No services found for the selected partner')
            else:
                service_main_line_ids = []
                service_main_order_ids = []
    
                for service in partner_id_data:
                    for line in service.service_line_ids:
                        _logger.info('line.invoice_id.invoice_number {}'.format(line.invoice_id.invoice_number))
                        _logger.info('line.invoice_id.invoice_prefix {}'.format(line.invoice_id.invoice_prefix))
                        service_main_line_ids.append((0, 0, {
                            'item_description': line.item_description,
                            'invoice_id': line.invoice_id.id,
                            # Fix the conditional expression with proper parentheses
                            'invoice_number': (line.invoice_id.invoice_prefix if line.invoice_id.invoice_prefix else '') + '-' + (line.invoice_id.invoice_number if line.invoice_id.invoice_number else ''),
                            'client_name': line.client_name.id,
                        }))
                
                
                if sale_order_data:
                    for order in sale_order_data:
                        self.amount_untaxed = order.amount_untaxed
                        self.amount_tax = order.amount_tax
                        self.amount_total = order.amount_total
                        for line in order.order_line:
                            service_main_order_ids.append((0, 0, {
                                'item_description': line.product_id.name,
                                'available': line.available,
                                'product_uom_qty': line.product_uom_qty,
                                'product_uom': line.product_uom.id,
                                'price_unit': line.price_unit,
                                'tax_id': [(6, 0, line.tax_id.ids)], 
                                'discount': line.discount,
                                'dex_selling_price': line.dex_selling_price,
                                'price_total': line.price_total,
                            }))
                else:
                    self.amount_untaxed = 0
                    self.amount_tax = 0
                    self.amount_total = 0
                
                self.service_main_line_ids = service_main_line_ids
                self.service_main_sale_order = service_main_order_ids
        else:
            self.amount_untaxed = 0
            self.amount_tax = 0
            self.amount_total = 0
            self.service_main_line_ids = [(5, 0, 0)]
            self.service_main_sale_order = [(5, 0, 0)]


            

class ServiceMainLine(models.TransientModel):
    _name = 'service.main.line'
    _description = 'Dex Service Line'

    service_main_id = fields.Many2one('dex_service.service.main', string='Service Id', ondelete='cascade')
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

    service_type = fields.Many2one('dex_service.service.type', string='Service Type', store=True)
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
    
    invoice_number = fields.Char(string='Invoice Number')
    
    
class ServiceMainSaleOrder(models.TransientModel):
    _name = 'service.main.sale.order'
    _description = 'Dex Service sale order'
    
    service_main_id = fields.Many2one('dex_service.service.main', string='Service Id', ondelete='cascade')
    item_description = fields.Char(string='Item Description')
    available = fields.Char(string='Available')
    product_uom_qty = fields.Integer(string='Qty')
    product_uom = fields.Many2one('uom.uom',string='Uom')
    price_unit = fields.Float(string='Price Unit')
    tax_id = fields.Many2one('account.taxt', string='Tax Id')
    discount = fields.Float(string='Discount')
    dex_selling_price = fields.Float(string='Dex Selling Price')
    price_total = fields.Float(string='Price Total')
    
    
    
    
    