from odoo import fields, models, api


class InheritPurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'
    _description = 'Inherit Purchase Requisition'

    pr_attachments = fields.One2many('purchase.requisition.attachments', 'pr_ids', 'Purchase Request Attachments')
    buyer = fields.Many2one('res.users', string='Buyer')

    def print_purchase_requests_form(self):
        return self.env.ref('approval_module_extension.purchase_request_report_id').report_action(self)
