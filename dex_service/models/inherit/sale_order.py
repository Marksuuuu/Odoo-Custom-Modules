# -*- coding: utf-8 -*-
import logging
from collections import defaultdict

from odoo import models, fields, _, api
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


# pylint: disable=no-member

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order Inherit'
    
    
    service_ids = fields.Many2one('service', string='Service Ids')
    what_type = fields.Selection(
        [('by_invoice', 'By Invoice'), ('by_warranty', 'By Warranty'), ('by_edp_code', 'By EDP-Code')], default=False,
        string='Type')