from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class DexServiceRequestForm(models.Model):
    _name = 'dex.service.request.form'
    _description = 'Dex Service Request Form'
    _order = 'id desc'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    # _description = 'Dex Service Request Form'
    
    name = fields.Char(string='Control No.', copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), tracking=True)

    dex_service_request_form_line_ids = fields.One2many('dex.service.request.form.line', 'dex_service_request_form_id')
    
    sales_coordinator = fields.Many2one('hr.employee', string='Sales Coordinator')

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
    
    what_type = fields.Selection(
        [('by_invoice', 'By Invoice'), ('by_warranty', 'By Warranty'), ('by_edp_code', 'By EDP-Code'),('by_edp_code_not_existing', 'By EDP-Code (Not Existing)')], default=False,
        string='Type')
    
    brand_units = fields.Many2one('uom.uom',string='Unit of Measure')
    number_of_units = fields.Integer(string='Number of Units')
    sale_order_no = fields.Many2one('sale.order',string='Sale Order')
    date_of_purchase = fields.Datetime(string='Date of Purchase')
    
    is_created = fields.Boolean(default=False)
    
    
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('dex.service.form.sequence.sfs') or '/'
        
        return super(DexServiceRequestForm, self).create(vals)
        
    @api.model
    def find_or_create_record(self, search_criteria, default_values):
        existing_records = self.env['service'].search(search_criteria)
    
        if existing_records:
            for record in existing_records:
                record.write(default_values)
            records = existing_records
        else:
            record = self.env['service'].create(default_values)
            records = self.env['service'].browse(record.id)
        service_line_ids = default_values.pop('service_line_ids', [])
        if service_line_ids:
            for line in service_line_ids:
                if isinstance(line, dict):
                    filtered_line = {
                        'edp_code': line.get('edp_code'),
                        'description': line.get('description'),
                    }
                    if isinstance(records, self.env['service']):
                        records = self.env['service'].browse(records.ids)
                    for record in records:
                        self.env['service.line'].create({
                            'service_id': record.id,
                            **filtered_line
                        })
        
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'type': 'success',
                'message': 'Created Successfully',
                'sticky': False,
            }
         }
        return notification


    def action_find_or_create(self):
        search_criteria = [('partner_id', '=', self.partner_id.id)]
        service_line_ids = self.dex_service_request_form_line_ids

        default_values = {
            'partner_id': self.partner_id.id,
            'service_line_ids': [(0, 0, {
                'client_name': self.partner_id.id,
                # 'edp_code': line.edp_code.id if line.edp_code else False,
                'item_description': line.description,
            }) for line in service_line_ids]
        }
        self.write({'is_created': True})
        return self.find_or_create_record(search_criteria, default_values)

        
    
class DexServiceRequestFormLine(models.Model):
    _name = 'dex.service.request.form.line'
    # _description = 'Dex Service Request Form Line'
    
    dex_service_request_form_id = fields.Many2one('dex.service.request.form', string='Service Request Form')
    
    edp_code = fields.Many2one('product.template',string='EDP-Code', domain=[('default_code', '!=', False)])
    
    description = fields.Char(related='edp_code.name')
    

    
    
    
    