from odoo import fields, models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    _description = 'Mrp Production'

    date_code = fields.Char(string='Date Code')
    case_no = fields.Integer(string='Case No.')

