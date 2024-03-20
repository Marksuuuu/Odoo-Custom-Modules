from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    wiv_picklist = fields.Selection([
        ('wiv', 'WIV'),
        ('picklist', 'Picklist'),
    ], string='WIV or Picklist?', default=False)

    reflect_pt = fields.Boolean(string='Reflect in PT?', default=False)

    @api.constrains('name')
    def _check_unique_product_name(self):
        for rec in self:
            if rec.name:
                existing_product = self.search([
                    ('name', '=', rec.name),
                    ('id', '!=', rec.id)
                ])
                if existing_product:
                    # Check if the name contains "(copy)"
                    if "(copy)" not in rec.name:
                        # If not, add "(copy)" to the name and re-check uniqueness
                        new_name = f"{rec.name} (copy)"
                        existing_product_with_copy = self.search([
                            ('name', '=', new_name),
                            ('id', '!=', rec.id)
                        ])
                        if existing_product_with_copy:
                            raise exceptions.ValidationError("Product with the same name already exists.")
                        else:
                            # Update the name of the current record
                            rec.write({'name': new_name})
