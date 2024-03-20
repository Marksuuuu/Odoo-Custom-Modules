from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Description'

    perishable = fields.Boolean(string='Perishable')
    non_perishable = fields.Boolean(string='Non-Perishable')
