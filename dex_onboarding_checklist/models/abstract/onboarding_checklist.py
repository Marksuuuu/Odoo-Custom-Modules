from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class OnboardingChecklist(models.AbstractModel):
    _name = 'onboarding.checklist'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Abstract model for Onboarding IT Checklist Form'

    def _get_department_domain(self):
        return []

    name = fields.Char(string='Control No.', copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))

    state = fields.Selection(
        selection=[('draft', 'Draft'), ('ongoing', 'Ongoing'), ('done', 'Done')],
        default='draft')

    requesters_id = fields.Many2one('hr.employee', string='Requesters', required=False,
                                    default=lambda self: self.env.user.employee_id.id)

    dex_emp_type = fields.Selection(related='requesters_id.dex_emp_type')

    requesters_email = fields.Char(related='requesters_id.work_email', string='Requesters Email',
                                   store=True)

    requesters_department = fields.Many2one(related='requesters_id.department_id', string='Requesters Department',
                                            store=True, required=False)

    # to be overridden by child models

    department_id = fields.Many2one('approver.setup', string='Department', domain=lambda a: a._get_department_domain(),
                                    tracking=True, required=True)

    form_request_type = fields.Selection(related='department_id.approval_type', string='Form Request Type', store=True,
                                         readonly=True)

    iden = fields.Char(string='ID')

    worker = fields.Many2many('hr.employee', string='Worker')

    task = fields.Char(string='Task')

    location = fields.Char(string='Location')

    start = fields.Datetime(string='Start')

    done = fields.Boolean(string='Done')

    rowguid = fields.Char(string='Row GUID')

    assigned_by = fields.Many2one('res.users', string='Assigned By')

    remarks = fields.Text(string='Remarks')

    estimate = fields.Float(string='Estimate')

    groups = fields.Char(string='Groups')

    reference_type = fields.Char(string='Reference Type')

    reference_id = fields.Integer(string='Reference ID')

    total_min = fields.Float(string='Total Minutes')

    work_id = fields.Char(string='Work Order')

    branch = fields.Char(string='Branch')

    worker2 = fields.Char(string='Worker 2')

    brand_desc = fields.Char(string='Brand Description')

    special_inst = fields.Text(string='Special Instructions')

    move_order_no = fields.Char(string='Move Order Number')

    so_no = fields.Char(string='Sales Order Number')

    priority_level = fields.Selection(
        [('critical', 'Critical'), ('urgent', 'Urgent'), ('within_a_week', 'Within a Week'),
         ('anytime', 'Anytime'), ('specified_date', 'Specified Date')], default=False, string='Priority Level')

    task_desc = fields.Text(string='Task Description')

    date_needed = fields.Date(string='Date Needed')

    initial_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    second_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    third_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    fourth_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    final_approver_job_title = fields.Char(compute='get_approver_title', store=True)

    approval_stage = fields.Integer(default=1)
    approval_link = fields.Char(string='Approval Link')

    initial_approver_email = fields.Char(string='Initial Approver Email')
    second_approver_email = fields.Char(string='Second Approver Email')
    third_approver_email = fields.Char(string='Third Approver Email')
    fourth_approver_email = fields.Char(string='Fourth Approver Email')
    final_approver_email = fields.Char(string='Final Approver Email')

    initial_approver_name = fields.Char(string='Initial Approver Name')
    second_approver_name = fields.Char(string='Second Approver Name')
    third_approver_name = fields.Char(string='Third Approver name')
    fourth_approver_name = fields.Char(string='Fourth Approver name')
    final_approver_name = fields.Char(string='Final Approver name')


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
