from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    dex_emp_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly')], default=False)

    hired_date = fields.Date(string='Hired Date')
    onboard_date = fields.Date(string='Onboard Date')

    is_lateral_transfer = fields.Boolean(default=False)

