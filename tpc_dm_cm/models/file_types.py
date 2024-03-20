from odoo import fields, models, api


class FileTypes(models.Model):
    _name = 'file.types'
    _description = 'Description'
    _rec_name = 'name'

    name = fields.Char()
