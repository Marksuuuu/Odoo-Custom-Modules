# -*- coding: utf-8 -*-
import logging
from collections import defaultdict

from odoo import models, fields, _, api
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


# pylint: disable=no-member

class WarehouseOrder(models.Model):
    _inherit = 'warehouse.order'
    _description = 'Transfer Order'

    department_id = fields.Many2one('approver.setup', string='Department', domain=lambda a: a._get_department_domain(),
                                    tracking=True)

    task = fields.Char()

    priority_level = fields.Selection(
        [('critical', 'Critical'), ('urgent', 'Urgent'), ('within_a_week', 'Within a Week'),
         ('anytime', 'Anytime'), ('specified_date', 'Specified Date')], default=False, string='Priority Level')

    jrf_id = fields.Many2one('job.request')

    def _get_department_domain(self):
        approval_types = self.env['approver.setup'].search([('approval_type', '=', 'job_request')])
        if approval_types:
            return [('id', 'in', approval_types.ids)]

    def action_confirm(self):
        self.write({
            'state': 'order',
            'confirmation_date': fields.Datetime.now()
        })
        self.create_job_request()

    def test(self):
        _logger.info('testtttttt')

    def create_job_request(self):
        # Mapping of the selection values for priority_level
        selection_mapping = {
            'critical': 'critical',
            'urgent': 'urgent',
            'within_a_week': 'within_a_week',
            'anytime': 'anytime',
            'specified_date': 'specified_date'
        }
        # Get the update_value from the mapping, defaulting to an empty string if not found
        update_value = selection_mapping.get(self.priority_level, '')

        _logger.info(f'ADDDDDDDDDDDDDDDDDD {update_value}')

        if self.with_jo:
            new_record = self.env['job.request'].create({
                'state': 'queue',
                'connection_wo': self.id,
                'requesters_id': self.env.user.employee_id.id,
                'department_id': self.department_id.id,
                'location': self.multi_transfer_warehouses_text,
                'special_inst': self.jo_instructions,
                'task': 'N/A',
                'priority_level': update_value,
                'workers_requested': self.jo_assigned_to,
                'date_needed': self.jo_date_needed,
            })
            self._create_job_request_connection(new_record)
            return new_record
        else:
            new_record = self.env['job.request'].create({
                'connection_wo': self.id,
                'requesters_id': self.env.user.employee_id.id,
                'department_id': self.department_id.id,
                'location': self.multi_transfer_warehouses_text,
                'special_inst': self.jo_instructions,
                'task': 'N/A',
                'priority_level': update_value,
                'date_needed': self.jo_date_needed,

            })
            self._create_job_request_connection(new_record)
            return new_record

    def _create_job_request_connection(self, id):
        create = self.jrf_id = id
        return create
