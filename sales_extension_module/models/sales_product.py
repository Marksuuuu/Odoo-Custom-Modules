from odoo import fields, models, api


class SalesProduct(models.Model):
    _name = 'sales.product'
    _description = 'Sales Product Maintenance'

    partner_id = fields.Many2one('res.partner', string='Customer', domain="[('parent_id', '=', False)]", )
    line_ids = fields.One2many('sales.product.line', 'sales_product', string='Connection')


class SalesProductLine(models.Model):
    _name = 'sales.product.line'
    _description = 'Sales Product Line'

    sales_product = fields.Many2one('sales.product', string='Sales Product')
    product_id = fields.Many2one('product.template', string='Product')
    description = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity')
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})
    # price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)

    # price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    # product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)

    @api.onchange('product_id')
    def product_onchange(self):
        for rec in self.product_id:
            self.description = "[{}] {}".format('' if rec.default_code is False else rec.default_code, rec.name)
            self.quantity = '' if rec.list_price is False else rec.list_price
            self.price_unit = '' if rec.standard_price is False else rec.standard_price
            self.product_uom = '' if rec.uom_id is False else rec.uom_id.id
