from odoo import fields, models, api, _


class ReportTemplateSetup(models.Model):
    _name = 'report.template.setup'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Report Template Setup'

    name = fields.Char(string='Report seq no.', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), tracking=True)
    customers = fields.Many2many('res.partner', string='Customers', tracking=True)
    associated_reports = fields.Many2one('ir.actions.report', string="Associated Reports", tracking=True)
    models_name = fields.Char(related='associated_reports.model', string='Associated Models')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('report.template.code') or '/'

        record = super(ReportTemplateSetup, self).create(vals)
        return record
