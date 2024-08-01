from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class JobAbstract(models.AbstractModel):
    _name = 'job.abstract'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Abstract model for Job Request Form'

    def _get_department_domain(self):
        return []

    name = fields.Char(string='Control No.', copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), tracking=True)

    state = fields.Selection(
        selection=[('draft', 'Draft'), ('queue', 'Queue'), ('assigned', 'Assigned'),
                   ('ongoing', 'Ongoing'), ('on_hold', 'On Hold'), ('cancelled', 'Cancelled'), ('rejected', 'Rejected'),
                   ('done', 'Done')],
        default='draft', tracking=True)

    requesters_id = fields.Many2one('hr.employee', string='Requesters', required=False,
                                    default=lambda self: self.env.user.employee_id.id, tracking=True)
    requesters_email = fields.Char(related='requesters_id.work_email', string='Requesters Email', tracking=True,
                                   store=True)
    requesters_department = fields.Many2one(related='requesters_id.department_id', string='Requesters Department',
                                            store=True, tracking=True, required=False)

    department_id = fields.Many2one('approver.setup', string='Department', domain=lambda a: a._get_department_domain(),
                                    tracking=True)

    form_request_type = fields.Selection([
        ('official_business', 'Official Business Form'),
        ('it_request', 'IT Request Form'),
        ('overtime_authorization', 'Overtime Authorization'),
        ('gasoline_allowance', 'Gasoline Allowance'),
        ('online_purchases', 'Online Purchases'),
        ('cash_advance', 'Request for Cash Advance'),
        ('grab_request', 'Grab Request Form'),
        ('client_pickup', 'Client Pickup Permit'),
        ('payment_request', 'Payment Request'),
        ('job_request', 'Job Request')], string='Form Request Type', store=True,
        readonly=True, tracking=True, default='job_request')

    iden = fields.Char(string='ID', tracking=True)

    worker = fields.Many2many('hr.employee', string='Worker', tracking=True)

    task = fields.Char(string='Task', tracking=True)

    location = fields.Char(string='Location')

    start = fields.Datetime(string='Start', tracking=True)

    done = fields.Boolean(string='Done', tracking=True)

    rowguid = fields.Char(string='Row GUID', tracking=True)

    assigned_by = fields.Many2one('res.users', string='Assigned By', tracking=True)

    remarks = fields.Text(string='Remarks', tracking=True)

    estimate = fields.Float(string='Estimate', tracking=True)

    groups = fields.Char(string='Groups', tracking=True)

    reference_type = fields.Char(string='Reference Type', tracking=True)

    reference_id = fields.Integer(string='Reference ID', tracking=True)

    total_min = fields.Float(string='Total Minutes', tracking=True)

    work_id = fields.Char(string='Work Order', tracking=True)

    branch = fields.Char(string='Branch', tracking=True)

    worker2 = fields.Char(string='Worker 2', tracking=True)

    brand_desc = fields.Char(string='Brand Description', tracking=True)

    special_inst = fields.Text(string='Special Instructions', tracking=True)

    move_order_no = fields.Char(string='Move Order Number', tracking=True)

    so_no = fields.Char(string='Sales Order Number', tracking=True)

    priority_level = fields.Selection(
        [('critical', 'Critical'), ('urgent', 'Urgent'), ('within_a_week', 'Within a Week'),
         ('anytime', 'Anytime'), ('specified_date', 'Specified Date')], default=False, string='Priority Level')

    task_desc = fields.Text(string='Task Description', tracking=True)

    date_needed = fields.Date(string='Date Needed', tracking=True)

    initial_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    second_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    third_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    fourth_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    final_approver_job_title = fields.Char(compute='get_approver_title', store=True)

    approval_stage = fields.Integer(default=1, tracking=True)
    approval_link = fields.Char(string='Approval Link')

    initial_approver_email = fields.Char(string='Initial Approver Email', tracking=True)
    second_approver_email = fields.Char(string='Second Approver Email', tracking=True)
    third_approver_email = fields.Char(string='Third Approver Email', tracking=True)
    fourth_approver_email = fields.Char(string='Fourth Approver Email', tracking=True)
    final_approver_email = fields.Char(string='Final Approver Email', tracking=True)

    initial_approver_name = fields.Char(string='Initial Approver Name', tracking=True)
    second_approver_name = fields.Char(string='Second Approver Name', tracking=True)
    third_approver_name = fields.Char(string='Third Approver name', tracking=True)
    fourth_approver_name = fields.Char(string='Fourth Approver name', tracking=True)
    final_approver_name = fields.Char(string='Final Approver name', tracking=True)

    def main_connection(self):
        # Load credentials from a secure source
        sender = self.env['ir.config_parameter'].sudo().get_param('dex_form_request_approval.sender')
        host = self.env['ir.config_parameter'].sudo().get_param('dex_form_request_approval.host')
        port = self.env['ir.config_parameter'].sudo().get_param('dex_form_request_approval.port')
        username = self.env['ir.config_parameter'].sudo().get_param('dex_form_request_approval.username')
        password = self.env['ir.config_parameter'].sudo().get_param('dex_form_request_approval.password')

        credentials = {
            'sender': sender,
            'host': host,
            'port': port,
            'username': username,
            'password': password
        }
        return credentials

    @api.depends('initial_approver_name', 'second_approver_name', 'third_approver_name', 'fourth_approver_name',
                 'final_approver_name')
    def get_approver_title(self):
        for record in self:
            if record.initial_approver_name:
                approver = self.env['hr.employee'].search([('name', '=', record.initial_approver_name)], limit=1)
                record.initial_approver_job_title = approver.job_title if approver else False

            if record.second_approver_name:
                approver = self.env['hr.employee'].search([('name', '=', record.second_approver_name)], limit=1)
                record.second_approver_job_title = approver.job_title if approver else False

            if record.third_approver_name:
                approver = self.env['hr.employee'].search([('name', '=', record.third_approver_name)], limit=1)
                record.third_approver_job_title = approver.job_title if approver else False

            if record.fourth_approver_name:
                approver = self.env['hr.employee'].search([('name', '=', record.fourth_approver_name)], limit=1)
                record.fourth_approver_job_title = approver.job_title if approver else False

            if record.final_approver_name:
                approver = self.env['hr.employee'].search([('name', '=', record.final_approver_name)], limit=1)
                record.final_approver_job_title = approver.job_title if approver else False
