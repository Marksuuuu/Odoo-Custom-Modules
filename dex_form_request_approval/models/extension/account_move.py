from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_request_ids = fields.Many2one('payment.request.form')
    transport_network_vehicle_ids = fields.Many2one('payment.request.form')
    mode_of_disbursement = fields.Selection([('cash', 'Cash'), ('check', 'Check')], string="Mode of Disbursement",
                                            tracking=True)
    sales_channel = fields.Many2one('crm.team', string="Sales Team", tracking=True)

