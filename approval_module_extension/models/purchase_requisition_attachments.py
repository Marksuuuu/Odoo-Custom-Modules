from odoo import fields, models, api


class PurchaseRequisitionAttachments(models.Model):
    _name = 'purchase.requisition.attachments'
    _description = 'Description'

    pr_ids = fields.Many2one('purchase.requisition', string="Purchase Requests Ids")
    product_id = fields.Many2one('product.product', string='Product')
    attachments_ids = fields.Many2one('ir.attachment', string='Attachments')
    file_links = fields.Char(string='File Links')