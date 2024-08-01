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

    approval_type_form = fields.Selection([
        ('official_business', 'Official Business Form'),
        ('it_request', 'IT Request Form'),
        ('overtime_authorization', 'Overtime Authorization'),
        ('gasoline_allowance', 'Gasoline Allowance'),
        ('online_purchases', 'Online Purchases'),
        ('cash_advance', 'Request for Cash Advance'),
        ('grab_request', 'Grab Request Form'),
        ('client_pickup', 'Client Pickup Permit'),
        ('payment_request', 'Payment Request'),
        ('job_request', 'Job Request'),
    ], string='Form Types', required=False)

    jrf_id = fields.Many2one('job.request')

    def _get_department_domain(self):
        approval_types = self.env['approver.setup'].search([('approval_type', '=', 'job_request')])
        if approval_types:
            return [('id', 'in', approval_types.ids)]

    def test_get(self):
        pass

    def get_task(self):
        items = []
        for rec in self.order_line:
            name = rec['name']  # Access name attribute

            items.append(name)  # Append a tuple of (product_id, name) to items

        return items  # Return the list of tuples containing (product_id, name) pairs

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

        form_types = {
            'official_business': 'official_business',
            'it_request': 'it_request',
            'overtime_authorization': 'overtime_authorization',
            'gasoline_allowance': 'gasoline_allowance',
            'online_purchases': 'online_purchases',
            'cash_advance': 'cash_advance',
            'grab_request': 'grab_request',
            'client_pickup': 'client_pickup',
            'payment_request': 'payment_request',
            'job_request': 'job_request',
        }
        # Get the update_value from the mapping, defaulting to an empty string if not found
        update_value_form = form_types.get(self.approval_type_form, 'job_request')

        existing_record = self.env['job.request'].search([('connection_wo', '=', self.id)])

        if existing_record:
            existing_record.write({
                'state': 'queue',
                'requesters_id': self.user_id.employee_id.id,
                'department_id': self.department_id.id,
                'location': self.multi_transfer_warehouses_text,
                'special_inst': self.jo_instructions,
                'task': 'N/A' if not self.get_task() else ', '.join(self.get_task()),
                'priority_level': update_value,
                'workers_requested': self.jo_assigned_to,
                'date_needed': self.jo_date_needed,
                'form_request_type': update_value_form,
            })
            # self._create_job_request_connection(existing_record)
            return existing_record
        else:
            new_record = self.env['job.request'].create({
                'state': 'queue',
                'connection_wo': self.id,
                'requesters_id': self.user_id.employee_id.id,
                'department_id': self.department_id.id,
                'location': self.multi_transfer_warehouses_text,
                'special_inst': self.jo_instructions,
                'task': 'N/A' if not self.get_task() else ', '.join(self.get_task()),
                'priority_level': update_value,
                'date_needed': self.jo_date_needed,
                'form_request_type': update_value_form,
            })
            self._create_job_request_connection(new_record)
            return new_record

    def _create_job_request_connection(self, id):
        create = self.jrf_id = id
        return create
