from odoo import models, fields, api, _
import base64
import pandas as pd
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DexServiceAddService(models.TransientModel):
    _name = 'dex_service.add.service'

    assign_request_line_ids = fields.One2many('dex_service.assign.request.line', 'assign_request_id')
    assign_request_service_time_ids = fields.One2many('dex_service.assign.request.service.time', 'assign_request_id')
    assign_request_other_details_ids = fields.One2many('dex_service.assign.request.other.details', 'assign_request_id')
    service = fields.Many2one('service.line')

    service_id = fields.Many2one('dex_service.service.line.thread', string='Client Name', domain=[('is_scheduled', '=', False)])
    partner_name = fields.Many2one(related='service_id.client_name', string='Client Name')
    pending_reason = fields.Char(related='service_id.pending_reason', string='Pending Reason')
    requesters_id = fields.Many2one(related='service_id.requesters_id', string='Requested By')
    free_of_charge = fields.Boolean(related='service_id.free_of_charge', string='Free of Charge')
    complaints = fields.Char(related='service_id.complaints', string='Complaints')
    item_description = fields.Char(related='service_id.item_description',string='Item Description')
    purchase_date = fields.Date(related='service_id.purchase_date', string='Purchase Date')
    with_warranty = fields.Boolean(related='service_id.with_warranty', default=False)
    # service_type = fields.Boolean(related='service_id.service_type', default=False)
    service_type = fields.Many2one(related='service_id.service_type', string='Service Type')
    # amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', tracking=4)


    def btn_save_changes(self):
        active_id = self._context.get('active_id')
        active_model = self.env.context.get('active_model')
        requests_res = self.env[active_model].browse(active_id)

        if not requests_res:
            requests_res.assign_request_line_ids = [(5, 0, 0)]
            requests_res.assign_request_service_time_ids = [(5, 0, 0)]
            requests_res.assign_request_other_details_ids = [(5, 0, 0)]
            return

        service_id = self.service_id.id if self.service_id else None
        partner_id = self.partner_name.id if self.partner_name else None
        free_of_charge = self.free_of_charge if self.free_of_charge else None
        requesters_id = self.requesters_id.id if self.requesters_id else None
        pending_reason = self.pending_reason if self.pending_reason else None
        complaints = self.complaints if self.complaints else None
        item_description = self.item_description if self.item_description else None
        purchase_date = self.purchase_date if self.purchase_date else None
        with_warranty = self.with_warranty if self.with_warranty else None
        service_type = self.service_type.id if self.service_type else None

        if self.service_id.service_line_main_ids.is_inputs_complete:
            if partner_id:
                new_line = {
                    'service_id': service_id,
                    'partner_id': partner_id
                    }
                new_line_service_time_ids = {
                    'partner_id': partner_id,
                    'service_id': service_id,
                    'pending_reason': pending_reason,
                    'free_of_charge': free_of_charge
                    }
                new_line_other_details_ids = {
                    'partner_id': partner_id,
                    'service_id': service_id,
                    'requesters_id': requesters_id,
                    'complaints': complaints,
                    'item_description': item_description,
                    'purchase_date': purchase_date,
                    'with_warranty': with_warranty,
                    'service_type': service_type,
                }
                assign_request_line_ids = [(0, 0, new_line) for _ in requests_res]
                assign_request_service_time_ids = [(0, 0, new_line_service_time_ids) for _ in requests_res]
                assign_request_other_details_ids = [(0, 0, new_line_other_details_ids) for _ in requests_res]

                requests_res.assign_request_line_ids = assign_request_line_ids
                requests_res.assign_request_service_time_ids = assign_request_service_time_ids
                requests_res.assign_request_other_details_ids = assign_request_other_details_ids
                requests_res.service_id = self.service_id.id

                service_record = self.env['dex_service.service.line.thread'].browse(service_id)
                service_record.write({'is_scheduled': True})
            else:
                requests_res.assign_request_line_ids = [(5, 0, 0)]
                requests_res.assign_request_service_time_ids = [(5, 0, 0)]
                requests_res.assign_request_other_details_ids = [(5, 0, 0)]
        else:
            msg = f'Please Contact {requests_res.service_id.service_line_main_ids.create_uid.name} to Finish/To Fully Filled this Fields (Pending Reason, Tentative Date, Contact/Phone Number), Thank you'
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'type': 'danger',
                    'message': msg,
                    'sticky': True,
                }
            }

            return notification

    def _assign_request(self, assign_request_line):
        self._update_add_service_time_records(assign_request_line)
        self._update_add_other_details_records(assign_request_line)
        self._update_add_service_details_records(assign_request_line)

    def _update_add_service_time_records(self, assign_request_line):
        if not isinstance(assign_request_line, list):
            assign_request_line = [assign_request_line]

        existing_ids = {line.partner_id.id for line in self.assign_request_service_time_ids}
        new_records = []

        for record in assign_request_line:
            partner_id = record.id
            if partner_id and partner_id not in existing_ids:
                new_records.append((0, 0, {
                    'partner_id': partner_id,
                }))

        if new_records:
            self.assign_request_service_time_ids = [(5, 0, 0)] + new_records
        else:
            self.assign_request_service_time_ids = [(5, 0, 0)]

    def _update_add_other_details_records(self, assign_request_line):
        existing_ids = {line.partner_id.id for line in self.assign_request_other_details_ids}
        new_records = []
        for record in assign_request_line:
            partner_id = record.id
            if partner_id and partner_id not in existing_ids:
                new_records.append((0, 0, {
                    'partner_id': partner_id,
                    # 'pending_reason': pending_reason,
                }))
        if new_records:
            self.assign_request_other_details_ids = [(0, 0, line[2]) for line in new_records]

    def _update_add_service_details_records(self, assign_request_line):
        existing_ids = {line.partner_id.id for line in self.assign_request_line_ids}
        new_records = []
        for record in assign_request_line:
            partner_id = record.id
            if partner_id and partner_id not in existing_ids:
                new_records.append((0, 0, {
                    'partner_id': partner_id,
                }))
        if new_records:
            self.assign_request_line_ids = [(0, 0, line[2]) for line in new_records]