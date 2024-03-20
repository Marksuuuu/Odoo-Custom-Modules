from odoo import fields, models, api


class PurchaseAgreements(models.Model):
    _inherit = 'purchase.requisition'
    _description = 'Inherited Purchase Requisition'

    buyer = fields.Char()
