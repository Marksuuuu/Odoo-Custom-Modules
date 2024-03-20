from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    lot_number = fields.Char(string="Lot Number", store=True)

