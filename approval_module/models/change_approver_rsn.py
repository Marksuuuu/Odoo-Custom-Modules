from odoo import fields, models, api, _


class ChangeApproverRsn(models.Model):
    _name = "change.approver.rsn"

    name = fields.Char(string="Reason")
    approval_type = fields.Many2one('purchase.approval.types')
    date = fields.Date(string="Date of Change", default=lambda self: self._context.get('date', fields.Date.context_today(self)))

