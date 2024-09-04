from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class AssignRequest(models.Model):
    _name = 'assign.request'
    _rec_name = 'service_id'

    assign_request_line_ids = fields.One2many('assign.request.line', 'assign_request_id')
    assign_request_service_time_ids = fields.One2many('assign.request.service.time', 'assign_request_id')
    assign_request_other_details_ids = fields.One2many('assign.request.other.details', 'assign_request_id')
    service_id = fields.Many2one('service.line', string='Service Id', ondelete='cascade')
    call_date = fields.Datetime(string='Call Date')
    technician = fields.Many2one('hr.employee', string='Technician')
    report_print_count = fields.Integer(string='Report Print Count', default=0)
    
    @api.onchange('assign_request_line_ids')
    def _onchange_assign_request_line_ids(self):
        if self.assign_request_line_ids:
            self._update_service_time_records()
            self._update_other_details_records()
    
    def _update_records(self, record_field, service_time_field):
        existing_ids = {line.partner_id.id for line in getattr(self, record_field)}
        new_records = []
        for record in self.assign_request_line_ids:
            partner_id = record.partner_id.id
            if partner_id and partner_id not in existing_ids:
                new_records.append((0, 0, {
                    'partner_id': partner_id,
                }))
        if new_records:
            setattr(self, service_time_field, [(0, 0, line[2]) for line in new_records])
            
    # def check_count_of_report_print_count(self):
    #     total_count = 0  
    #     for rec in self:
    #         total_count += rec.report_print_count  
    #     return total_count

            
            
    # def _update_service_time_records(self):
    #     existing_ids = {line.partner_id.id for line in self.assign_request_service_time_ids}
    #     new_records = []
    #     for record in self.assign_request_line_ids:
    #         partner_id = record.partner_id.id
    #         if partner_id and partner_id not in existing_ids:
    #             new_records.append((0, 0, {
    #                 'partner_id': partner_id,
    #             }))
    #     if new_records:
    #         self.assign_request_service_time_ids = [(0, 0, line[2]) for line in new_records]
    # 
    # def _update_other_details_records(self):
    #     existing_ids = {line.partner_id.id for line in self.assign_request_other_details_ids}
    #     new_records = []
    #     for record in self.assign_request_line_ids:
    #         partner_id = record.partner_id.id
    #         if partner_id and partner_id not in existing_ids:
    #             new_records.append((0, 0, {
    #                 'partner_id': partner_id,
    #             }))
    #     if new_records:
    #         self.assign_request_other_details_ids = [(0, 0, line[2]) for line in new_records]
    
    def _update_service_time_records(self):
        self._update_records('assign_request_service_time_ids', 'assign_request_service_time_ids')
    
    def _update_other_details_records(self):
        self._update_records('assign_request_other_details_ids', 'assign_request_other_details_ids')


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
            
    def print_service_report(self):
        # List to hold report actions for each record
        report_actions = []
    
        # Unlink all records where report_print_count == 0
        records_to_unlink = self.search([('report_print_count', '=', 0)])
        if records_to_unlink:
            records_to_unlink.unlink()
            _logger.info(f'Unlinked {len(records_to_unlink)} records because report_print_count was 0')
    
        # Iterate through each record in `self` to handle remaining ones
        for record in self:
            existing_records = self.search([('service_id', '=', record.service_id.id)])
            
            if existing_records:
                for existing_record in existing_records:
                    if existing_record.report_print_count > 0:
                        # Increment the report_print_count if it's greater than 0
                        existing_record.write({
                            'report_print_count': existing_record.report_print_count + 1
                        })
                        # Generate the report action for this record
                        report_action = self.env.ref('dex_service.service_odoo_report_id').report_action(existing_record)
                        report_actions.append(report_action)
            else:
                _logger.warning(f'No existing records found for service_id {record.service_id.id}')
    
        # Return combined actions if there are multiple
        if len(report_actions) == 1:
            return report_actions[0]
        elif len(report_actions) > 1:
            return {
                'type': 'ir.actions.act_multi',
                'actions': report_actions + [{'type': 'ir.actions.act_window_close'}]
            }
        else:
            return {
                'type': 'ir.actions.act_window_close'
            }






class AssignRequestLine(models.Model):
    _name = 'assign.request.line'

    assign_request_id = fields.Many2one('assign.request')
    partner_id = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)])
    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    city = fields.Char(related='partner_id.city')
    state_id = fields.Many2one(related='partner_id.state_id')
    zip = fields.Char(related='partner_id.zip')
    country_id = fields.Many2one(related='partner_id.country_id')
    type = fields.Selection(related='partner_id.type')
    user_id = fields.Many2one(related='partner_id.user_id')
    
    look_for = fields.Char(string='Look For')
    
    
    def main_func(self):
        pass

    
class AssignRequestServiceTime(models.Model):
    _name = 'assign.request.service.time'
    
    assign_request_id = fields.Many2one('assign.request')
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
    payment_type = fields.Selection([('cash', 'Cash'),('check', 'Check'),('bank', 'Bank'),('advance', 'Advance'),('credit', 'Credit'),('collection', 'Collection')],string='Payment Type')
    parts_defect = fields.Char(string='Parts Defect')
    parts_cost = fields.Integer(string='Parts Cost')
    parts_cost_actual = fields.Integer(string='Parts Cost Actual')
    peding_reason = fields.Char(string='Pending Reason')
    total = fields.Integer(string='Total')
    
    def main_func(self):
        pass

    
class AssignRequestOtherDetails(models.Model):
    _name = 'assign.request.other.details'

    assign_request_id = fields.Many2one('assign.request')
    partner_id = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)])
    item = fields.Many2one('product.template', string='Item')
    parts_request = fields.Char(string='Parts Request')
    parts_feedback = fields.Char(string='Parts Feedback')
    requested_by = fields.Many2one('hr.employee', string='Requested By')
    requested_date = fields.Datetime(string='Requested Date')
    customer_feedback = fields.Char(string='Customer Feedback')
    
    def main_func(self):
        pass
