from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class FromRequestTypes(models.Model):
    _name = 'form.request.types'
    _description = 'Description'

    @api.constrains('name')
    def _check_request_type(self):
        allowed_types = [
            'IT Request Form',
            'Job Request Form',
            'Request for Cash Advance',
            'Pickup Authorization Form',
            'Overtime Authorization Form',
            'Official Business Form',
            'Gasoline Allowance Form'
            'Transport Network Vehicle'
        ]
        for rec in self:
            if rec.name not in allowed_types:
                allowed_types_str = ', '.join(allowed_types)
                raise ValidationError(_('Invalid request type! Allowed types are: %s') % allowed_types_str)

    name = fields.Char()
