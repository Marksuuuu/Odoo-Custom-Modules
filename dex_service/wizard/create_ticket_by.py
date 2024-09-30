from odoo import models, fields, api
import base64
import pandas as pd
import logging
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class CreateTicketBy(models.TransientModel):
    _name = 'create.ticket.by'
    # _inherit = 'account.move'
    
    service_id = fields.Many2one('service', string='Service Id', ondelete='cascade')
    service_type = fields.Many2one('service.type', string='Service Type')
    
    what_type = fields.Selection(
        [('by_invoice', 'By Invoice'), ('by_warranty', 'By Warranty'), ('by_edp_code', 'By EDP-Code'),('by_edp_code_not_existing', 'By EDP-Code (Not Existing)')], default=False,
        string='Type')
    
    partner_id = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)])
    warranty_number = fields.Many2one('warranty',string='Warranty #')
    
    edp_code = fields.Many2many('product.template',string='EDP-Code', domain=[('default_code', '!=', False)])
    
    edp_code_not_existing = fields.Many2many('not.existing.product',string='EDP-Code')

    request_type = fields.Integer()
    
    ## Invoice NO Related Fields
    invoice_no = fields.Many2one('account.move', domain=[('type', '=', 'out_invoice')])

    # invoice_to_name = fields.Char(related='invoice_no.invoice_to_name', string='Invoice to Name')
    partner_id_invoice = fields.Many2one(related='invoice_no.partner_id', string='Invoice to Name')
    invoice_date = fields.Date(related='invoice_no.invoice_date', string='Invoice Date')
    # sale_order_id = fields.Many2one(related='invoice_no.sale_order_id', string='Invoice Date')
    
    status = fields.Selection(
        [('open', 'Open'), ('cancelled', 'Cancelled'),('close', 'Close'), ('pending', 'Pending'), ('waiting', 'Waiting')], default='open',
        string='Type')
    
    create_ticket_by_line_ids = fields.One2many('create.ticket.by.line', 'create_ticket_by_line_line_ids')
    
    # @api.onchange('warranty_number')
    # def onchange_warranty_number(self):
    #     self.invoice_no = self.warranty_number.invoice_no.id
    #     _logger.info('invoice_no {}'.format(self.warranty_number.invoice_no.id))
    #     if self.invoice_no:
    #         if not self.invoice_no.invoice_line_ids:
    #             _logger.info('No lines found in invoice_no')
    #             self.create_ticket_by_line_ids = [(5, 0, 0)]
    #         else:
    #             self.create_ticket_by_line_ids = [(5, 0, 0)]
    #             create_ticket_by_line_ids = []
    #             for line in self.warranty_number.warranty_line_ids:
    #                 create_ticket_by_line_ids.append((0, 0, {
    #                     'product_id': line.product_id.id,
    #                     'name': line.name,
    #                     'quantity': line.quantity,
    #                 }))
    #             self.create_ticket_by_line_ids = create_ticket_by_line_ids
    #     else:
    #         self.create_ticket_by_line_ids = [(5, 0, 0)]
    
    

    
    
    @api.onchange('invoice_no')
    def onchange_invoice_no(self):
        if self.invoice_no:
            if not self.invoice_no.invoice_line_ids:
                self.create_ticket_by_line_ids = [(5, 0, 0)]
            else:
                self.create_ticket_by_line_ids = [(5, 0, 0)]
                create_ticket_by_line_ids = []
                for line in self.invoice_no.invoice_line_ids:
                    create_ticket_by_line_ids.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'quantity': line.quantity,
                    }))
                self.create_ticket_by_line_ids = create_ticket_by_line_ids
        else:
            self.create_ticket_by_line_ids = [(5, 0, 0)]


    

    def btn_save_changes(self):
        active_id = self._context.get('active_id')
        active_model = self.env.context.get('active_model')
        requests_res = self.env[active_model].browse(active_id)
        
        if self.what_type == 'by_invoice':
            self.create_service_lines_invoice(requests_res)
        elif self.what_type == 'by_warranty':
            self.create_service_lines_warranty(requests_res)
        elif self.what_type == 'by_edp_code':
            self.create_service_lines_edp(requests_res)
        elif self.what_type == 'by_edp_code_not_existing':
            self.create_service_lines_edp_not_existing(requests_res)
        else:
            raise UserError('Type Required')
            
    
    def create_service_lines_warranty(self, requests_res):
        if not self.partner_id:
            raise UserError('Cannot proceed; you need to add a partner.')
        
        if not requests_res:
            raise UserError('No model IDs provided to update.')
        
        partner_id = self.partner_id.id
        service_id = self.service_id.id
        service_type_id = self.service_type.id
        what_type = self.what_type
        
        vals_list = []
        
        for line_id in self.warranty_number:
            vals = {
                'item_description': line_id.name,
                'service_id': service_id,
                'client_name': partner_id,
                'service_type': service_type_id,
                'what_type': what_type,
                'warranty_number': line_id.id,
            }
            vals_list.append(vals)
        service_lines = self.env['service.line'].create(vals_list)
        requests_res.write({
            'service_type': False,
        })
        
        return service_lines


    
    def create_service_lines_edp(self, requests_res):
        if not self.partner_id:
            raise UserError('Cannot proceed; you need to add a partner.')
        
        if not requests_res:
            raise UserError('No model IDs provided to update.')
        
        vals_list = []
        
        for line_id in self.edp_code:
            vals = {
                'item_description': line_id.name,
                'service_id': self.service_id.id,
                'client_name': self.partner_id.id,
                'service_type': self.service_type.id,
                'what_type': self.what_type,
            }
            vals_list.append(vals)
        
        service_lines = self.env['service.line'].create(vals_list)
        
        requests_res.write({
            'service_type': False,
        })
        
        return service_lines
    
    def create_service_lines_edp_not_existing(self, requests_res):
        if not self.partner_id:
            raise UserError('Cannot proceed; you need to add a partner.')
        
        if not requests_res:
            raise UserError('No model IDs provided to update.')
        
        vals_list = []
        
        for line_id in self.edp_code_not_existing:
            vals = {
                'item_description': line_id.name,
                'service_id': self.service_id.id,
                'client_name': self.partner_id.id,
                'service_type': self.service_type.id,
                'what_type': self.what_type,
            }
            vals_list.append(vals)
        
        service_lines = self.env['service.line'].create(vals_list)
        
        requests_res.write({
            'service_type': False,
        })
        
        return service_lines

    def create_service_lines_invoice(self, requests_res):
        if not self.partner_id:
            raise UserError('Cannot proceed; you need to add a partner.')
        
        if not requests_res:
            raise UserError('No model IDs provided to update.')
        
        vals_list = []
        
        for line_id in self.create_ticket_by_line_ids: 
            vals = {
                'item_description': line_id.name,
                'invoice_id': self.invoice_no.id,
                'purchase_date': self.invoice_date,
                'service_id': self.service_id.id,
                'client_name': self.partner_id.id,
                'service_type': self.service_type.id,
                'what_type': self.what_type,
            }
            vals_list.append(vals)
        
        service_lines = self.env['service.line'].create(vals_list)
        
        requests_res.write({
            'service_type': False,
        })
        
        return service_lines

    
class CreateTicketByLine(models.TransientModel):
    _name = 'create.ticket.by.line'
    
    
    create_ticket_by_line_line_ids = fields.Many2one('create.ticket.by')
    
    
    product_id = fields.Many2one('product.product')
    name = fields.Char()
    quantity = fields.Integer()
    
    
    def insert_as_ticket(self):
        _logger.info('testtingggg')