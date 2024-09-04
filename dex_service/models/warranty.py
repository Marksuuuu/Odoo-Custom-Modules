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


class Warranty(models.Model):
    _name = 'warranty'
    _description = 'Dex Service Warranty'
    
    
    warranty_line_ids = fields.One2many('warranty.line', 'warranty_id')
    
    name = fields.Char(string='Warranty No.', copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), tracking=True)
    
    customer_id = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)], required=True)

    street = fields.Char(related='customer_id.street')
    street2 = fields.Char(related='customer_id.street2')
    city = fields.Char(related='customer_id.city')
    state_id = fields.Many2one(related='customer_id.state_id')
    zip = fields.Char(related='customer_id.zip')
    country_id = fields.Many2one(related='customer_id.country_id')
    user_id = fields.Many2one(related='customer_id.user_id')
    type = fields.Selection(related='customer_id.type')
    
    edp_code = fields.Many2one('product.template',string='EDP-Code', domain=[('default_code', '!=', False)])

    serial_number = fields.Char(string='Serial Number')
    
    invoice_no = fields.Many2one('account.move', domain=[('type', '=', 'out_invoice')])
    
    @api.onchange('invoice_no')
    def onchange_invoice_no(self):
        if self.invoice_no:
            if not self.invoice_no.invoice_line_ids:
                _logger.info('No lines found in invoice_no')
                self.warranty_line_ids = [(5, 0, 0)] 
            else:
                self.warranty_line_ids = [(5, 0, 0)]
                warranty_line_ids = []
                for line in self.invoice_no.invoice_line_ids:
                    warranty_line_ids.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'quantity': line.quantity,
                    }))
                self.warranty_line_ids = warranty_line_ids
        else:
            self.warranty_line_ids = [(5, 0, 0)]

    
    
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('create.service.request.sequence.wrnty') or '/'
        
        return super(Warranty, self).create(vals)


class WarrantyLine(models.Model):
    _name = 'warranty.line'
    _description = 'warranty line'
    
    warranty_id = fields.Many2one('warranty')
    
    product_id = fields.Many2one('product.product')
    name = fields.Char()
    quantity = fields.Integer()
    
    
