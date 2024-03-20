from ast import literal_eval

from odoo import fields, models, api, _


class PurchaseApproval(models.Model):
    _name = "purchase.approval"
    _description = "Approvals"

    name = fields.Char(string='Approvals')
    approval_ids = fields.One2many('purchase.order', 'approval_id')
    approval_type_knbn = fields.Many2one('purchase.approval.types')




