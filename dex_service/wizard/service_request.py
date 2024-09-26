from odoo import models, fields, api, _
import base64
import pandas as pd
import logging

_logger = logging.getLogger(__name__)


class ServiceRequest(models.TransientModel):
    _name = 'service.request'
    
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
    
    
    
class ServiceLine(models.Model):
    _name = 'service.line'
    _description = 'Dex Service Line'
    
    
    service_id = fields.Many2one('service.request', string='Service Id', ondelete='cascade')
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
