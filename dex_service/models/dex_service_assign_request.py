from odoo import models, fields, api, _
import logging
from odoo.exceptions import UserError
import base64
import io
from PyPDF2 import PdfFileMerger, PdfFileReader
from datetime import datetime

_logger = logging.getLogger(__name__)


class DexServiceAssignRequest(models.Model):
    _name = 'dex_service.assign.request'
    _order = 'id desc'
    _rec_name = 'name'

    assign_request_line_ids = fields.One2many('dex_service.assign.request.line', 'assign_request_id')
    assign_request_service_time_ids = fields.One2many('dex_service.assign.request.service.time', 'assign_request_id')
    assign_request_other_details_ids = fields.One2many('dex_service.assign.request.other.details', 'assign_request_id')
    service_id = fields.Many2one('dex_service.service.line.thread', string='Client Name',
                                 domain=[('is_scheduled', '=', False)])
    report_print_count = fields.Integer(string='Report Print Count', default=0)

    transaction_date = fields.Datetime(string='Transaction Date')
    time_in = fields.Float(string='Time In')
    time_out = fields.Float(string='Time Out')

    name = fields.Char(string='Control No.', copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), tracking=True)

    technician = fields.Many2many('hr.employee', string='Technician')

    @api.onchange('technician')
    def _onchange_technician(self):
        categories = self.env['hr.job'].sudo().search([('name', '=', 'Service Technician')])
        if categories:
            return {'domain': {'technician': [('job_id', 'in', categories.ids)]}}
        else:
            return {'domain': {'technician': []}}

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('service.request.sr') or '/'
        return super(DexServiceAssignRequest, self).create(vals)

    @api.model
    def get_one2many_data(self, record_id):
        record = self.browse(record_id)
        if not record:
            return {}
        return {
            'assign_request_line_ids': [line for line in record.assign_request_line_ids],
            'assign_request_service_time_ids': [service_time for service_time in
                                                record.assign_request_service_time_ids],
            'assign_request_other_details_ids': [other_detail for other_detail in
                                                 record.assign_request_other_details_ids],
        }

    @api.model
    def get_all_data_as_list(self):
        result = {
            'assign_request_line_ids': [],
            'assign_request_service_time_ids': [],
            'assign_request_other_details_ids': [],
        }

        for record in self:
            result['assign_request_line_ids'].extend([line for line in record.assign_request_line_ids])
            result['assign_request_service_time_ids'].extend(
                [service_time for service_time in record.assign_request_service_time_ids])
            result['assign_request_other_details_ids'].extend(
                [details for details in record.assign_request_other_details_ids])

        return result

    def create_function(self):
        data = self.get_all_data_as_list()

        lines = data['assign_request_line_ids']
        service_times = data['assign_request_service_time_ids']
        other_details = data['assign_request_other_details_ids']

        for rec in lines.pop():
            _logger.info("rec IDs: %s", rec)

        _logger.info("Lines IDs: %s", lines.pop().partner_id.name)
        _logger.info("Service Times IDs: %s", service_times)
        _logger.info("Other Details IDs: %s", other_details)

        return data

    def print_both(self):
        merger = PdfFileMerger()

        # Generate the service report PDF
        service_report_pdf = self.env.ref('dex_service.service_odoo_report_id').render_qweb_pdf([self.id])[0]
        merger.append(io.BytesIO(service_report_pdf))
        _logger.info("First report appended.")

        if self.assign_request_line_ids:
            for rec in self.assign_request_line_ids:
                request_form_pdf = rec.service_id.print_service_request_form()
                acknowledgment_form_pdf = rec.service_id.print_acknowledgment_form()

                if request_form_pdf and acknowledgment_form_pdf:
                    merger.append(io.BytesIO(request_form_pdf))
                    merger.append(io.BytesIO(acknowledgment_form_pdf))
                    _logger.info("Request form PDF appended for record: %s", rec.id)
                else:
                    if not request_form_pdf:
                        _logger.warning("Request form PDF is empty or not generated for record: %s", rec.id)
                    if not acknowledgment_form_pdf:  # Log if acknowledgment PDF is empty
                        _logger.warning("Acknowledgment form PDF is empty or not generated for record: %s", rec.id)
        else:
            _logger.warning("No service request lines found.")

        output = io.BytesIO()
        merger.write(output)
        merger.close()

        output.seek(0)
        merged_pdf_reader = PdfFileReader(io.BytesIO(output.getvalue()))
        _logger.info("Merged PDF page count: %d", merged_pdf_reader.getNumPages())
        current_time = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        attachment = self.env['ir.attachment'].create({
            'name': 'Service_Combined_Report_{}.pdf'.format(current_time),
            'type': 'binary',
            'datas': base64.b64encode(output.read()).decode('utf-8'),
            'store_fname': 'combined_report.pdf',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }

    @api.onchange('assign_request_line_ids')
    def _onchange_assign_request_line_ids(self):
        if self.assign_request_line_ids:
            self._update_service_time_records()
            self._update_other_details_records()

    def _update_service_time_records(self):
        self._update_records('assign_request_service_time_ids', 'assign_request_service_time_ids')

    def _update_other_details_records(self):
        self._update_records('assign_request_other_details_ids', 'assign_request_other_details_ids')

    def _update_records(self, record_field, service_time_field):
        existing_ids = {line.partner_id.id for line in getattr(self, record_field)}
        new_records = []

        for record in self.assign_request_line_ids:
            partner_id = record.partner_id.id
            if partner_id and partner_id not in existing_ids:
                new_records.append((0, 0, {
                    'partner_id': partner_id,
                    'assign_request_line': record.id,
                }))
                _logger.info(
                    'Preparing to add new record with partner_id {} and assign_request_line_id {}'.format(partner_id,
                                                                                                          record.id))

        if new_records:
            new_values = [(0, 0, rec[2]) for rec in new_records]
            setattr(self, service_time_field, new_values)

    @api.onchange('service_id')
    def _onchange_service_id(self):
        for rec in self:
            if rec.service_id:
                assign_request_line = rec.service_id.client_name
                assign_request_line_id = fields.Datetime.now().strftime('%Y%m%d%H%M%S')
                rec._assign_request(assign_request_line, assign_request_line_id)
            else:
                rec.assign_request_service_time_ids = [(5, 0, 0)]

    def _assign_request(self, assign_request_line, assign_request_line_id):
        self._update_add_service_time_records(assign_request_line, assign_request_line_id)
        self._update_add_other_details_records(assign_request_line, assign_request_line_id)
        self._update_add_service_details_records(assign_request_line, assign_request_line_id)

    def _update_add_service_time_records(self, assign_request_line, assign_request_line_id):
        if not isinstance(assign_request_line, list):
            assign_request_line = [assign_request_line]

        existing_ids = {line.partner_id.id for line in self.assign_request_service_time_ids}
        new_records = []

        for record in assign_request_line:
            partner_id = record.id
            if partner_id and partner_id not in existing_ids:
                new_records.append((0, 0, {
                    'partner_id': partner_id,
                    'assign_request_line': assign_request_line_id,
                }))

        if new_records:
            self.assign_request_service_time_ids = [(5, 0, 0)] + new_records
        else:
            self.assign_request_service_time_ids = [(5, 0, 0)]

    def _update_add_other_details_records(self, assign_request_line, assign_request_line_id):
        existing_ids = {line.partner_id.id for line in self.assign_request_other_details_ids}
        new_records = []
        for record in assign_request_line:
            partner_id = record.id
            if partner_id and partner_id not in existing_ids:
                new_records.append((0, 0, {
                    'partner_id': partner_id,
                    'assign_request_line': assign_request_line_id,
                }))
        if new_records:
            self.assign_request_other_details_ids = new_records

    def _update_add_service_details_records(self, assign_request_line, assign_request_line_id):
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

    def btn_save_changes(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        if not active_id or not active_model:
            _logger.error("Active ID or Active Model is not present in context.")
            return

        requests_res = self.env[active_model].browse(active_id)

        if requests_res:
            vals = {
                'partner_id': self.partner_id.id,
            }
            requests_res.write(vals)

    # def print_service_report(self):
    # report_actions = []
    # records_to_unlink = self.search([('report_print_count', '=', 0)])
    # if records_to_unlink:
    #     records_to_unlink.unlink()
    #     _logger.info(f'Unlinked {len(records_to_unlink)} records because report_print_count was 0')
    #
    # for record in self:
    #     existing_records = self.search([('service_id', '=', record.service_id.id)])
    #
    #     if existing_records:
    #         for existing_record in existing_records:
    #             if existing_record.report_print_count > 0:
    #                 existing_record.write({
    #                     'report_print_count': existing_record.report_print_count + 1
    #                 })
    #                 report_action = self.env.ref('dex_service.service_odoo_report_id').report_action(existing_record)
    #                 report_actions.append(report_action)
    #     else:
    #         _logger.warning(f'No existing records found for service_id {record.service_id.id}')
    #
    # if len(report_actions) == 1:
    #     return report_actions[0]
    # elif len(report_actions) > 1:
    #     return {
    #         'type': 'ir.actions.act_multi',
    #         'actions': report_actions + [{'type': 'ir.actions.act_window_close'}]
    #     }
    # else:
    #     return {
    #         'type': 'ir.actions.act_window_close'
    #     }

    def add_service(self):
        action = {
            'name': 'Add Service',
            'type': 'ir.actions.act_window',
            'res_model': 'dex_service.add.service',
            'view_mode': 'form',
            'target': 'new',
            'domain': [],
            'context': {
                # 'default_service': self.service_id.id
            }
        }
        return action


class DexServiceAssignRequestLine(models.Model):
    _name = 'dex_service.assign.request.line'
    _order = 'id desc'

    assign_request_id = fields.Many2one('dex_service.assign.request')
    service_id = fields.Many2one('dex_service.service.line.thread', string='Thread')
    partner_id = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)])
    street = fields.Char(related='partner_id.street')
    fee = fields.Integer(string='Fee')
    street2 = fields.Char(related='partner_id.street2')
    city = fields.Char(related='partner_id.city')
    state_id = fields.Many2one(related='partner_id.state_id')
    zip = fields.Char(related='partner_id.zip')
    country_id = fields.Many2one(related='partner_id.country_id')
    type = fields.Selection(related='partner_id.type')
    user_id = fields.Many2one(related='partner_id.user_id')
    brand_id = fields.Many2one('dex_brand_series.brand')
    look_for = fields.Char(string='Look For')

    def main_func(self):
        pass

    def unlink(self):
        related_records = self.env['dex_service.service.line.thread'].search([('id', '=', self.service_id.id)])

        for record in related_records:
            record.write({'is_scheduled': False})

        service_time = self.env['dex_service.assign.request.service.time'].search(
            [('service_id', '=', self.service_id.id)])
        other_details = self.env['dex_service.assign.request.other.details'].search(
            [('service_id', '=', self.service_id.id)])

        service_time.unlink()
        other_details.unlink()

        return super(DexServiceAssignRequestLine, self).unlink()


class DexServiceAssignRequestServiceTime(models.Model):
    _name = 'dex_service.assign.request.service.time'
    _order = 'id desc'

    assign_request_id = fields.Many2one('dex_service.assign.request')
    service_id = fields.Many2one('dex_service.service.line.thread', string='Thread')
    assign_request_line = fields.Char()
    partner_id = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)])
    type = fields.Selection(related='partner_id.type')
    user_id = fields.Many2one(related='partner_id.user_id')
    job_request = fields.Char(string='Job Request')
    service_action = fields.Char(string='Action')
    service_cost = fields.Integer(string='Service Cost')
    payment_remarks = fields.Char(string='Payment / Remarks')
    time_in = fields.Float(string='Time In')
    time_out = fields.Float(string='Time Out')
    dr_no = fields.Char(string='DR No.')
    or_no = fields.Char(string='OR No.')
    payment_type = fields.Selection(
        [('cash', 'Cash'), ('check', 'Check'), ('bank', 'Bank'), ('advance', 'Advance'), ('credit', 'Credit'),
         ('collection', 'Collection')], string='Payment Type')
    parts_defect = fields.Char(string='Parts Defect')
    free_of_charge = fields.Boolean(string='Free of Charge')
    parts_cost = fields.Integer(string='Parts Cost')
    parts_cost_actual = fields.Integer(string='Parts Cost Actual')
    pending_reason = fields.Char(string='Pending Reason')
    total = fields.Integer(string='Total')

    def main_func(self):
        pass


class DexServiceAssignRequestOtherDetails(models.Model):
    _name = 'dex_service.assign.request.other.details'
    _order = 'id desc'

    assign_request_id = fields.Many2one('dex_service.assign.request')
    service_id = fields.Many2one('dex_service.service.line.thread', string='Thread')
    assign_request_line = fields.Char()
    partner_id = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)])
    item_description = fields.Char(string='Item Description')
    item = fields.Many2one('product.template', string='Item')
    parts_request = fields.Char(string='Parts Request')
    parts_feedback = fields.Char(string='Parts Feedback')
    requesters_id = fields.Many2one('res.users', string='Requested By')
    requested_date = fields.Datetime(string='Requested Date')
    customer_feedback = fields.Char(string='Customer Feedback')
    complaints = fields.Char(string='Complaints')
    call_date = fields.Datetime(string='Call Date')
    purchase_date = fields.Date(string='Purchase Date')
    with_warranty = fields.Boolean(default=False)
    remarks = fields.Text(string='Remarks')
    service_type = fields.Many2one('dex_service.service.type', string='Service Type')
    trouble_reported = fields.Char(string='Trouble Reported')

    item_count = fields.Integer(string='Item Count')
    item_price = fields.Integer(string='Item Price')

    def main_func(self):
        pass
