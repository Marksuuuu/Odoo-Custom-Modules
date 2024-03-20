from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'sale.order'
    _description = 'sale order inherit'

    ## This is for Customer be careful about this function
    @api.onchange('partner_id')
    def partner_id_onchange_domain(self):
        for rec in self:
            if rec.partner_id and rec._origin:  # Check if partner_id exists and record is not being created or deleted
                domain_invoice = [('parent_id', '=', rec.partner_id.id), ('type', '=', 'invoice')]
                domain_delivery = [('parent_id', '=', rec.partner_id.id), ('type', '=', 'delivery')]

                return {'domain': {
                    'partner_invoice_id': domain_invoice,
                    'partner_shipping_id': domain_delivery,
                }}
            else:
                return {'domain': {}}  # No partner_id, so no domain filters
