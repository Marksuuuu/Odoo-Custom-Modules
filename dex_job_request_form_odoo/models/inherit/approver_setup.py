# -*- coding: utf-8 -*-
import logging
from collections import defaultdict

from odoo import models, fields, _, api
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


# pylint: disable=no-member

class ApproverSetup(models.Model):
    _inherit = 'approver.setup'
    _description = 'Approver Setup Inherit'

    dept_name = fields.Many2one('hr.department', required=False)

    @api.onchange('approval_type')
    def onchange_approval_type(self):
        if self.approval_type == 'job_request':
            self.dept_name = False  # Set dept_name to no value (False, None, '', etc.)
