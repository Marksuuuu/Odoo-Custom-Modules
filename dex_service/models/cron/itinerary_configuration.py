from odoo import models, fields, api, _
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ItineraryConfiguration(models.Model):
    _name = 'itinerary.configuration'
    _order = 'id desc'

    email_groups = fields.Selection([('all@dexterton.loc', 'All'), ('bgc@dexterton.loc', 'Bgc'), ('qc@dexterton.loc', 'Qc')
                                     , ('warehouse@dexterton.loc', 'Warehouse'), ('specific_email', 'Specific Email')], string='Email Groups')

    specific_email = fields.Char(string='Email')


    @api.onchange('email_groups')
    def onchange_email_groups(self):
        if self.email_groups != 'specific_email':
            self.specific_email = False
