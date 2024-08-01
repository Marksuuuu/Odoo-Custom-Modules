from datetime import date, datetime
import hashlib
import re
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import formataddr
import json
import random

import logging

_logger = logging.getLogger(__name__)


class EmployeeOnboardingChecklist(models.Model):
    _name = 'employee.onboarding.checklist'
    _inherit = ['onboarding.checklist']

    approver_id = fields.Many2one('hr.employee', string="Approver", domain=lambda self: self.get_approver_domain(),
                                  store=True)

    history_ids = fields.One2many('history.log', 'record_id', string='History Logs',
                                  domain=[('model', '=', 'employee.onboarding.checklist')])

    approver_count = fields.Integer(compute='_compute_approver_count', store=True)
    check_status = fields.Char(compute='compute_check_status', store=True)

    approved_by = fields.Many2one('res.users', string="Approved By")
    date_approved = fields.Datetime()

    branch_location = fields.Selection([
        ('bgc', 'Bgc'),
        ('qc', 'Qc'),
        ('wh', 'WH')], default=False)

    is_approver = fields.Boolean(compute="compute_approver")

    requesters_email = fields.Char(related='requesters_id.work_email', string='Requesters Email', required=True)

    emp_name = fields.Many2one('hr.employee', string='Employee Name')
    is_lateral_transfer = fields.Boolean(default=False)
    gender = fields.Selection(related='emp_name.gender', string='Employee Name')
    login_name = fields.Char(related='emp_name.user_id.login_name', string='Nickname')
    birthday = fields.Date(related='emp_name.birthday', string='Birthday')
    job_id = fields.Many2one(related='emp_name.job_id', string='Position')
    first_name = fields.Char(string='First Name', compute='_compute_split_name', store=True)
    middle_name = fields.Char(string='Middle Name', compute='_compute_split_name', store=True)
    last_name = fields.Char(string='Last Name', compute='_compute_split_name', store=True)
    emp_id = fields.Char(string='Employee Id')
    bio_id = fields.Char(string='Biometric Id')

    date_hired = fields.Date(string='Date Hired')
    onboard_date = fields.Date(string='Onboard Date')

    ## Device Software

    computer_type = fields.Selection([
        ('standard_desktop', 'Standard Desktop'),
        ('highspec_desktop', 'High Spec Desktop'),
        ('standard_laptop', 'Standard Laptop'),
        ('highspec_laptop', 'High Spec Laptop')
    ])

    mobile = fields.Char(string='Mobile')
    is_mobile = fields.Boolean(default=False)

    tablet = fields.Char(string='Tablet')
    is_tablet = fields.Boolean()

    other_equipment_requests = fields.Char(string='Other Equipment Requests')

    operating_system = fields.Char(string='Operating System')
    ip_address = fields.Char(string='IP Address')

    is_adobe_cc = fields.Boolean()
    is_ms_office = fields.Boolean()

    other_software_requests = fields.Char(string='Other Software Requests')

    ## Accounts / Access

    local_email = fields.Char(string='Local Email')
    online_email = fields.Char(string='Online Email')

    is_domain_account = fields.Boolean()
    is_dicapps = fields.Boolean()
    is_discord = fields.Boolean()
    is_odoo = fields.Boolean()
    is_oracle = fields.Boolean()
    is_doris = fields.Boolean()
    is_vpn = fields.Boolean()

    other_email_account_requests = fields.Char(string='Other Email Account Requests')
    other_account_requests = fields.Char(string='Other Account Requests')

    ## Other Fields

    submitted_by = fields.Many2one('res.users', string='Submitted By', required=False,
                                    default=lambda self: self.env.user.id, tracking=True)
    process_by = fields.Many2one('res.user', string='Processed By')
    submitted_date = fields.Date(string='Submitted Date')
    process_date = fields.Date(string='Processed Date')

    current_user_groups1 = fields.Char(string='Current User Groups', compute='_compute_current_user_groups1')

    is_edited_by_hr = fields.Boolean(default=False)
    is_edited_by_it = fields.Boolean(default=False)

    revision_count = fields.Integer(string='Revision Count', compute='_compute_total_revision', default=0)

    @api.depends('revision_count')
    def _compute_total_revision(self):
        for record in self:
            history_count = self.env['history.log'].search_count(
                [('record_id', '=', record.id), ('name', '=', 'Updated record')])
            _logger.info('history_count {}'.format(history_count))
            record.revision_count = history_count

    def eoc_approval(self):
        request_form = self.env['employee.onboarding.checklist'].sudo().search(
            [('approval_link', '=', self.approval_link)])
        request_form.with_context({'no_log': True}).write({'is_edited_by_hr': True, 'is_edited_by_it': True})
        # request_form.is_edited_by_hr = True
        if request_form:
            request_form.approve_request()
            msg = "Request approved successfully!"
            return f"""<script>alert("{msg}");window.close();</script>"""
        else:
            return 'test'

    def open_form_view(self):
        view_id = self.env.ref('dex_onboarding_checklist.history_log_tree_view').id

        action = {
            'name': 'History',
            'type': 'ir.actions.act_window',
            'res_model': 'history.log',
            # 'views': [(view_id, 'tree')],
            'view_mode': 'tree,form',
            'target': 'current',
            # 'res_id': self.id,
            'domain': [('record_id', '=', self.id), ('name', '=', 'Updated record')],
            'context': {
                'create': False
            }

        }
        return action

    def default_converter(self, o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        return o

    def compute_approver(self):
        for rec in self:
            if self.env.user.name == rec.approver_id.name:
                self.update({
                    'is_approver': True,
                })
            else:
                self.update({
                    'is_approver': False,
                })

    @api.model
    def create(self, vals):
        # If the 'name' field is not provided, set it to the next sequence number
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('create.sequence.form.sequence.eoc') or '/'

        # Create the record using the super method
        record = super(EmployeeOnboardingChecklist, self).create(vals)

        # Create a history log record
        self.env['history.log'].sudo().create({
            'name': 'Created record',
            'model': self._name,
            'record_id': record.id,
            'user_id': self.env.uid,
            'changes': json.dumps(vals, default=self.default_converter),
            'tracked_record': f'{self._name},{record.id}'
        })
        # self._notify_email(self.get_emails_by_department(), self.env.user.name, 'create')

        return record

    def write(self, vals):
        if not self.env.context.get('no_log', False):
            changes = {}
            records = self.read(list(vals.keys()))
            old_values = {record['id']: {k: record[k] for k in vals.keys()} for record in records}

            res = super(EmployeeOnboardingChecklist, self).write(vals)

            records = self.read(list(vals.keys()))
            new_values = {record['id']: {k: record[k] for k in vals.keys()} for record in records}

            for record in self:
                record_changes = {}
                record_id = record.id

                for key in vals.keys():
                    old_value = old_values.get(record_id, {}).get(key)
                    new_value = new_values.get(record_id, {}).get(key)
                    if old_value != new_value:
                        record_changes[key] = {
                            'old': old_value,
                            'new': new_value
                        }

                if record_changes:
                    self.env['history.log'].sudo().create({
                        'name': 'Updated record',
                        'model': self._name,
                        'record_id': record.id,
                        'user_id': self.env.uid,
                        'changes': json.dumps(record_changes, default=self.default_converter),
                        'tracked_record': f'{self._name},{record.id}'
                    })
                    self._notify_email(self.get_emails_by_department(), self.env.user.name, 'edit')
            return res
        else:
            return super(EmployeeOnboardingChecklist, self).write(vals)

    def unlink(self):
        history_logs = self.env['history.log'].sudo().search([('record_id', 'in', self.ids)])
        self._notify_email(self.get_emails_by_department(), self.env.user.name, 'delete')

        history_logs.unlink()  # Delete the associated history records

        return super(EmployeeOnboardingChecklist, self).unlink()  # Proceed with the unlink operation

    def get_emails_by_department(self):
        department_name = 'IT Dept.'
        department = self.env['hr.department'].search([('name', '=', department_name)], limit=1)

        if department:
            employees = self.env['hr.employee'].search([('department_id', '=', department.id)])

            employee_emails = [employee.work_email for employee in employees if employee.work_email]

            return employee_emails
        else:
            return f"No department found with name {department_name}"

    @api.depends('emp_name')
    def _compute_split_name(self):
        for record in self:
            if record.emp_name:
                full_name = record.emp_name.name or ''
                name_parts = full_name.split()
                record.first_name = name_parts[0] if len(name_parts) > 0 else ''
                record.middle_name = ' '.join(name_parts[1:-1]) if len(name_parts) > 2 else ''
                record.last_name = name_parts[-1] if len(name_parts) > 1 else ''

    def _get_department_domain(self):
        approval_types = self.env['approver.setup'].search([('approval_type', '=', 'onboarding_checklist')])
        if approval_types:
            return [('id', 'in', approval_types.ids)]

    @api.onchange('requesters_id')
    def _onchange_requesters_id(self):
        if self.requesters_id and self.requesters_id.department_id:
            department_name = self.requesters_id.department_id.name
            approval_type = 'onboarding_checklist'

            # Search for the approver.setup record matching department name and approval type
            approver_setup = self.env['approver.setup'].search([
                ('approval_type', '=', approval_type),
                ('dept_name.name', '=', department_name)
            ], limit=1)

            if approver_setup:
                self.department_id = approver_setup.id
            else:
                self.department_id = None

    def compute_approver(self):
        for rec in self:
            if self.env.user.name == rec.approver_id.name:
                self.update({
                    'is_approver': True,
                })
            else:
                self.update({
                    'is_approver': False,
                })

    def submit_for_approval(self):
        # Approval Dashboard Link Section
        approval_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        approval_action = self.env['ir.actions.act_window'].search(
            [('name', '=', 'Client Pickup Permit')], limit=1)
        action_id = approval_action.id

        odoo_params = {
            "action": action_id,
        }

        query_string = '&'.join([f'{key}={value}' for key, value in odoo_params.items()])
        approval_list_view_url = f"{approval_base_url}/web?debug=0#{query_string}"

        # Generate Odoo Link Section
        odoo_action = self.env['ir.actions.act_window'].search([('res_model', '=', 'employee.onboarding.checklist')],
                                                               limit=1)
        odoo_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        odoo_result = re.sub(r'\((.*?)\)', '', str(odoo_action)).replace(',', '')
        odoo_res = f"{odoo_result},{odoo_action.id}"
        odoo_result = re.sub(r'\s*,\s*', ',', odoo_res)

        odoo_menu = self.env['ir.ui.menu'].search([('action', '=', odoo_result)], limit=1)
        odoo_params = {
            "id": self.id,
            "action": odoo_action.id,
            "model": "client.pick.up.permit",
            "view_type": "form",
            "cids": 1,
            "menu_id": odoo_menu.id
        }
        odoo_query_params = "&".join(f"{key}={value}" for key, value in odoo_params.items())
        form_link = f"{odoo_base_url}/web#{odoo_query_params}"

        get_all_email_receiver = self.approver_id.work_email

        recipient_list = []
        if self.department_id and self.department_id.set_first_approvers:
            for approver in self.department_id.set_first_approvers:
                if approver.approver_email:
                    recipient_list.append(approver.approver_email)

        self.sending_email(recipient_list, form_link, approval_list_view_url)
        # self.sending_email(get_all_email_receiver, form_link, approval_list_view_url)

        self.with_context({'no_log': True}).write({
            'state': 'ongoing',
        })

    @api.depends('state')
    def compute_check_status(self):
        recipient_list = []
        get_jrf_requestor = self.env['approver.setup'].search([('approval_type', '=', 'onboarding_checklist')])
        if self.form_request_type == 'onboarding_checklist':
            for approver in get_jrf_requestor.set_second_approvers:
                if approver.approver_email:
                    recipient_list.append(approver.approver_email)
        if self.requesters_email:
            recipient_list.append(self.requesters_email)

        _logger.info('recipient_list {}'.format(recipient_list))

        for rec in self:
            if rec.state == 'ongoing':
                # rec.notify_to_all(recipient_list)
                _logger.info('GOING TO ONGOING')
            elif rec.state == 'done':
                _logger.info('GOING TO DONE')
                rec.notify_to_all(recipient_list)
            else:
                pass

    def get_approvers_in_list(self):
        email_list = []
        for rec in self.department_id:
            for key in ['set_first_approvers', 'set_second_approvers', 'set_third_approvers', 'set_fourth_approvers',
                        'set_fifth_approvers']:
                approver_list = getattr(rec, key, [])
                for data in approver_list:
                    for val in ['first_approver', 'second_approver', 'third_approver', 'fourth_approver',
                                'fifth_approver']:
                        res = getattr(data, val, None)
                        if res and res.work_email:  # Check if work_email exists
                            email_list.append(res.work_email)
        return email_list

    def generate_token(self):
        now = datetime.now()
        token = "{}-{}-{}-{}".format(self.id, self.name, self.env.user.id, now)
        return hashlib.sha256(token.encode()).hexdigest()

    @api.depends('approval_stage')
    def approve_request(self):
        for rec in self:

            res = self.env["approver.setup"].search([
                ("dept_name", "=", rec.department_id.dept_name.name),
                ("approval_type", '=', rec.form_request_type)
            ])

            if rec.state == 'ongoing':
                if rec.approver_id and rec.approval_stage < res.no_of_approvers:
                    if rec.approval_stage == 1:

                        if self.initial_approver_name is None:
                            raise UserError('No approver set')
                        else:
                            self.with_context({'no_log': True}).write({
                                'initial_approver_name': rec.approver_id.name
                            })
                            # self.initial_approver_name = rec.approver_id.name

                        approver_dept = [x.second_approver.id for x in res.set_second_approvers]

                        self.with_context({'no_log': True}).write({
                            'approver_id': approver_dept[0]
                        })

                        recipient_list = []
                        if self.department_id and self.department_id.set_second_approvers:
                            for approver in self.department_id.set_second_approvers:
                                if approver.approver_email:
                                    recipient_list.append(approver.approver_email)

                        self.submit_to_next_approver(recipient_list)
                        self.save_current_date()

                    if rec.approval_stage == 2:
                        if self.second_approver_name is None:
                            raise UserError('No approver set')
                        else:
                            self.with_context({'no_log': True}).write({
                                'second_approver_name': rec.approver_id.name
                            })
                            # self.second_approver_name = rec.approver_id.name
                        approver_dept = [x.third_approver.id for x in res.set_third_approvers]

                        self.with_context({'no_log': True}).write({
                            'approver_id': approver_dept[0]
                        })

                        recipient_list = []
                        if self.department_id and self.department_id.set_third_approvers:
                            for approver in self.department_id.set_third_approvers:
                                if approver.approver_email:
                                    recipient_list.append(approver.approver_email)

                        self.submit_to_next_approver(recipient_list)
                        self.save_current_date()

                    if rec.approval_stage == 3:
                        if self.third_approver_name is None:
                            raise UserError('No approver set')
                        else:
                            # self.third_approver_name = rec.approver_id.name
                            self.with_context({'no_log': True}).write({
                                'third_approver_name': rec.approver_id.name
                            })

                        approver_dept = [x.fourth_approver.id for x in res.set_fourth_approvers]

                        self.with_context({'no_log': True}).write({
                            'approver_id': approver_dept[0]
                        })

                        recipient_list = []
                        if self.department_id and self.department_id.set_fourth_approvers:
                            for approver in self.department_id.set_fourth_approvers:
                                if approver.approver_email:
                                    recipient_list.append(approver.approver_email)

                        self.submit_to_next_approver(recipient_list)
                        self.save_current_date()

                    if rec.approval_stage == 4:
                        if self.fourth_approver_name is None:
                            raise UserError('No approver set')
                        else:
                            self.with_context({'no_log': True}).write({
                                'fourth_approver_name': rec.approver_id.name
                            })
                            # self.fourth_approver_name = rec.approver_id.name

                        approver_dept = [x.fifth_approver.id for x in res.set_fifth_approvers]

                        self.with_context({'no_log': True}).write({
                            'approver_id': approver_dept[0]
                        })

                        recipient_list = []
                        if self.department_id and self.department_id.set_fifth_approvers:
                            for approver in self.department_id.set_fifth_approvers:
                                if approver.approver_email:
                                    recipient_list.append(approver.approver_email)

                        self.submit_to_next_approver(recipient_list)
                        self.save_current_date()

                    rec.with_context({'no_log': True}).approval_stage += 1
                else:
                    self.with_context({'no_log': True}).write({
                        'state': 'done',
                        'is_edited_by_it': False,
                        'final_approver_name': rec.approver_id.name,
                        'approval_link': ''
                    })
                    self.save_current_date()
            else:
                print('approval status else: ', rec.state)

    def save_current_date(self):
        date_now = datetime.now()
        formatted_date = date_now.strftime("%m/%d/%Y")

        self.date_today = formatted_date

        if self.initial_approver_name:
            self.initial_approval_date = formatted_date

        if hasattr(self, 'second_approver_name') and self.second_approver_name:
            self.second_approval_date = formatted_date

        if hasattr(self, 'third_approver_name') and self.third_approver_name:
            self.third_approval_date = formatted_date

        if hasattr(self, 'fourth_approver_name') and self.fourth_approver_name:
            self.fourth_approval_date = formatted_date

        if hasattr(self, 'final_approver_name') and self.final_approver_name:
            self.final_approval_date = formatted_date

    def generate_odoo_link(self):
        # Generate Odoo Link Section
        action = self.env['ir.actions.act_window'].search([('res_model', '=', 'employee.onboarding.checklist')],
                                                          limit=1)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        result = re.sub(r'\((.*?)\)', '', str(action)).replace(',', '')
        res = f"{result},{action.id}"
        result = re.sub(r'\s*,\s*', ',', res)

        menu = self.env['ir.ui.menu'].search([('action', '=', result)], limit=1)
        params = {
            "id": self.id,
            "action": action.id,
            "model": "employee.onboarding.checklist",
            "view_type": "form",
            "cids": 1,
            "menu_id": menu.id
        }
        query_params = "&".join(f"{key}={value}" for key, value in params.items())
        form_link = f"{base_url}/web#{query_params}"
        return form_link

    def submit_to_next_approver(self, approver_to_send):
        # Approval Dashboard Link Section

        approval_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        approval_action = self.env['ir.actions.act_window'].search(
            [('name', '=', 'Onboarding Request Form')], limit=1)
        action_id = approval_action.id
        odoo_params = {
            "action": action_id,
        }

        query_string = '&'.join([f'{key}={value}' for key, value in odoo_params.items()])
        approval_list_view_url = f"{approval_base_url}/web?debug=0#{query_string}"

        # Generate Odoo Link Section
        odoo_action = self.env['ir.actions.act_window'].search([('res_model', '=', 'employee.onboarding.checklist')],
                                                               limit=1)
        odoo_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        odoo_result = re.sub(r'\((.*?)\)', '', str(odoo_action)).replace(',', '')
        odoo_res = f"{odoo_result},{odoo_action.id}"
        odoo_result = re.sub(r'\s*,\s*', ',', odoo_res)

        odoo_menu = self.env['ir.ui.menu'].search([('action', '=', odoo_result)], limit=1)
        odoo_params = {
            "id": self.id,
            "action": odoo_action.id,
            "model": "employee.onboarding.checklist",
            "view_type": "form",
            "cids": 1,
            "menu_id": odoo_menu.id
        }
        odoo_query_params = "&".join(f"{key}={value}" for key, value in odoo_params.items())
        form_link = f"{odoo_base_url}/web#{odoo_query_params}"

        self.generate_odoo_link()
        self.approval_dashboard_link()

        get_all_email_receiver = self.approver_id.work_email  # <-- This Code are for One approver set only
        self.sending_email_to_next_approver(approver_to_send)

        # self.with_context({'no_log':True}).write({
        #     'state': 'to_approve',
        # })

    def notify_to_all(self, recipient_list):
        conn = self.main_connection()
        sender = conn['sender']
        host = conn['host']
        port = conn['port']
        username = conn['username']
        password = conn['password']

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        token = self.generate_token()

        approval_url = "{}/dex_onboarding_checklist/request/cpp_approve/{}".format(base_url, token)
        disapproval_url = "{}/dex_onboarding_checklist/request/cpp_disapprove/{}".format(base_url, token)

        self.with_context({'no_log': True}).write({'approval_link': token})
        msg = MIMEMultipart()

        msg['From'] = formataddr(('Odoo Mailer', sender))

        msg['To'] = ', '.join(recipient_list)
        msg['Subject'] = (
            f"{re.sub(r'[-_]', ' ', self.form_request_type).title() if self.state else ''} "
            f"Request has been {str(self.state).title() if self.state else ''} "
            f"[{str(self.name)}]"
        )

        html_content = """
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Multiple Tables</title>
                        <style>
                                    /* Basic styling for the page */
                            body {
                                font-family: Arial, sans-serif;
                                margin: 20px;
                            }

                            /* Basic styling for all tables */
                            table {
                                border-collapse: collapse;
                                width: 100%;
                                margin-bottom: 20px;
                            }

                            th, td {
                                border: 1px solid #ddd;
                                padding: 8px;
                                text-align: left;
                                width: 300px;
                            }

                            th {
                                background-color: #0068AD;
                                color: white;
                            }

                            tr:nth-child(even) {
                                background-color: #f2f2f2;
                            }

                            tr:hover {
                                background-color: #ddd;
                            }

                            /* Specific styles for individual tables */
                            .table-1x2, .table-3x4, .table-2x1 {
                                width: auto;
                            }

                            /* Styled link as button */
                            .link-button {
                                display: inline-block;
                                background-color: #0068AD;
                                color: white;
                                padding: 10px 20px;
                                text-align: center;
                                text-decoration: none;
                                font-size: 16px;
                                border-radius: 4px;
                                margin-top: 20px;
                            }

                             .link-button:hover {
                                background-color: #45a049;
                            }

                            .link-button::after {
                                content: "";
                                position: absolute;
                                top: 50%;
                                left: 50%;
                                transform: translate(-50%, -50%);
                                width: 100px; /* Adjust size as needed */
                                height: 100px; /* Adjust size as needed */
                                background-size: cover;
                                opacity: 0;
                                transition: opacity 0.3s ease;
                            }

                            .link-button:hover::after {
                                opacity: 1;
                            }

                            /* Title styling */
                            .title {
                                font-size: 24px;
                                font-weight: bold;
                                margin-bottom: 20px;
                            }
                        </style>
                    </head>"""
        html_content += f"""<body>
                          <div class="title">Employee Onboarding Checklist {'(' + self.name + ')'}</div>

                        <!-- 3x4 Table -->
                        <table class="table-3x4">
                            <thead>
                                <tr>
                                    <th colspan="2">Employee Type</th>
                                    <th colspan="2">Branch / Location</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td colspan="2">{self.dex_emp_type if self.dex_emp_type else ''}</td>
                                    <td colspan="2">{self.branch_location if self.branch_location else ''}</td>
                                </tr>
                            </tbody>
                            <thead>
                                <tr>
                                    <th colspan="4">Employee Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Name</td>
                                    <td>{self.emp_name.name if self.emp_name else ''}</td>
                                    <td>Gender</td>
                                    <td>{self.birthday if self.birthday else ''}</td>
                                </tr>
                                <tr>
                                    <td>Nickname</td>
                                    <td>{self.login_name if self.login_name else ''}</td>
                                    <td>Employee ID</td>
                                    <td>{self.emp_id if self.emp_id else ''}</td>
                                </tr>
                                <tr>
                                    <td>Biometric ID</td>
                                    <td>{self.bio_id if self.bio_id else ''}</td>
                                    <td>Position</td>
                                    <td>{self.job_id if self.job_id else ''}</td>
                                </tr>
                                <tr>
                                    <td colspan="2">Onboard Date</td>
                                    <td colspan="2">{self.onboard_date.strftime("%m-%d-%y") if self.onboard_date else ''}</td>
                                </tr>

                            </tbody>
                            <thead>
                                <tr>
                                    <th colspan="4">Other Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Submitted By</td>
                                    <td colspan="3">{self.requesters_id.name if self.requesters_id else ''}</td>
                                </tr>
                                <tr>
                                    <td>Submitted Date</td>
                                    <td colspan="3">{self.submitted_date.strftime("%m-%d-%y") if self.submitted_date else ''}</td>
                                </tr>

                            </tbody>
                        </table>"""

        html_content += """</body>
                    </html>

                """
        msg.attach(MIMEText(html_content, 'html'))

        try:
            smtpObj = smtplib.SMTP(host, port)
            smtpObj.login(username, password)
            smtpObj.sendmail(sender, recipient_list, msg.as_string())

            msg = "Successfully sent email"
            _logger.info('msg {}'.format(msg))
            return {
                'success': {
                    'title': 'Successfully email sent!',
                    'message': f'{msg}'}
            }
        except Exception as e:
            msg = f"Error: Unable to send email: {str(e)}"
            _logger.info('msg {}'.format(msg))
            return {
                'warning': {
                    'title': 'Error: Unable to send email!',
                    'message': f'{msg}'}
            }

    def sending_email(self, get_all_email_receiver, form_link, approval_list_view_url):
        conn = self.main_connection()
        sender = conn['sender']
        host = conn['host']
        port = conn['port']
        username = conn['username']
        password = conn['password']

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        token = self.generate_token()

        approval_url = "{}/dex_onboarding_checklist/request/cpp_approve/{}".format(base_url, token)
        disapproval_url = "{}/dex_onboarding_checklist/request/cpp_disapprove/{}".format(base_url, token)

        self.with_context({'no_log': True}).write({'approval_link': token})
        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))
        msg['To'] = ', '.join(get_all_email_receiver)
        msg[
            'Subject'] = f"{re.sub(r'[-_]', ' ', self.form_request_type).title() if self.state else ''} Request for Approval [{self.name}]"

        html_content = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Multiple Tables</title>
                <style>
                            /* Basic styling for the page */
                    body {
                        font-family: Arial, sans-serif;
                        margin: 20px;
                    }
            
                    /* Basic styling for all tables */
                    table {
                        border-collapse: collapse;
                        width: 100%;
                        margin-bottom: 20px;
                    }
            
                    th, td {
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                        width: 300px;
                    }
            
                    th {
                        background-color: #0068AD;
                        color: white;
                    }
            
                    tr:nth-child(even) {
                        background-color: #f2f2f2;
                    }
            
                    tr:hover {
                        background-color: #ddd;
                    }
            
                    /* Specific styles for individual tables */
                    .table-1x2, .table-3x4, .table-2x1 {
                        width: auto;
                    }
            
                    /* Styled link as button */
                    .link-button {
                        display: inline-block;
                        background-color: #0068AD;
                        color: white;
                        padding: 10px 20px;
                        text-align: center;
                        text-decoration: none;
                        font-size: 16px;
                        border-radius: 4px;
                        margin-top: 20px;
                    }
            
                     .link-button:hover {
                        background-color: #45a049;
                    }
            
                    .link-button::after {
                        content: "";
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        width: 100px; /* Adjust size as needed */
                        height: 100px; /* Adjust size as needed */
                        background-size: cover;
                        opacity: 0;
                        transition: opacity 0.3s ease;
                    }
            
                    .link-button:hover::after {
                        opacity: 1;
                    }
            
                    /* Title styling */
                    .title {
                        font-size: 24px;
                        font-weight: bold;
                        margin-bottom: 20px;
                    }
                </style>
            </head>"""
        html_content += f"""<body>
                  <div class="title">Employee Onboarding Checklist {'(' + self.name + ')'}</div>
            
                <!-- 3x4 Table -->
                <table class="table-3x4">
                    <thead>
                        <tr>
                            <th colspan="2">Employee Type</th>
                            <th colspan="2">Branch / Location</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td colspan="2">{self.dex_emp_type.title() if self.dex_emp_type else ''}</td>
                            <td colspan="2">{self.branch_location.title() if self.branch_location else ''}</td>
                        </tr>
                    </tbody>
                    <thead>
                        <tr>
                            <th colspan="4">Employee Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Name</td>
                            <td>{self.emp_name.name.title() if self.emp_name else ''}</td>
                            <td>Gender</td>
                            <td>{self.birthday if self.birthday else ''}</td>
                        </tr>
                        <tr>
                            <td>Nickname</td>
                            <td>{self.login_name.title() if self.login_name else ''}</td>
                            <td>Employee ID</td>
                            <td>{self.emp_id if self.emp_id else ''}</td>
                        </tr>
                        <tr>
                            <td>Biometric ID</td>
                            <td>{self.bio_id if self.bio_id else ''}</td>
                            <td>Position</td>
                            <td>{self.job_id if self.job_id else ''}</td>
                        </tr>
                        <tr>
                            <td colspan="2">Onboard Date</td>
                            <td colspan="2">{self.onboard_date.strftime("%m-%d-%y") if self.onboard_date else ''}</td>
                        </tr>
            
                    </tbody>
                    <thead>
                        <tr>
                            <th colspan="4">Other Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Submitted By</td>
                            <td colspan="3">{self.requesters_id.name.title() if self.requesters_id else ''}</td>
                        </tr>
                        <tr>
                            <td>Submitted Date</td>
                            <td colspan="3">{self.submitted_date.strftime("%m-%d-%y") if self.submitted_date else ''}</td>
                        </tr>
            
                    </tbody>
                </table>
            
                 <a href="{self.generate_odoo_link()}" class="link-button">Edit Request Now</a>"""

        html_content += """</body>
            </html>

        """

        msg.attach(MIMEText(html_content, 'html'))

        try:
            smtpObj = smtplib.SMTP(host, port)
            smtpObj.login(username, password)
            smtpObj.sendmail(sender, get_all_email_receiver, msg.as_string())

            msg = "Successfully sent email"
            return {
                'success': {
                    'title': 'Successfully email sent!',
                    'message': f'{msg}'}
            }
        except Exception as e:
            msg = f"Error: Unable to send email: {str(e)}"
            return {
                'warning': {
                    'title': 'Error: Unable to send email!',
                    'message': f'{msg}'}
            }

    def sending_email_to_next_approver(self, get_all_email_receiver):
        conn = self.main_connection()
        sender = conn['sender']
        host = conn['host']
        port = conn['port']
        username = conn['username']
        password = conn['password']

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        token = self.generate_token()

        approval_url = "{}/dex_onboarding_checklist/request/cpp_approve/{}".format(base_url, token)
        disapproval_url = "{}/dex_onboarding_checklist/request/cpp_disapprove/{}".format(base_url, token)

        self.with_context({'no_log': True}).write({'approval_link': token})
        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))
        msg['To'] = ', '.join(get_all_email_receiver)
        msg[
            'Subject'] = f"{re.sub(r'[-_]', ' ', self.form_request_type).title() if self.state else ''} Request for Approval [{self.name}]"

        html_content = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Multiple Tables</title>
                <style>
                            /* Basic styling for the page */
                    body {
                        font-family: Arial, sans-serif;
                        margin: 20px;
                    }

                    /* Basic styling for all tables */
                    table {
                        border-collapse: collapse;
                        width: 100%;
                        margin-bottom: 20px;
                    }

                    th, td {
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                        width: 300px;
                    }

                    th {
                        background-color: #0068AD;
                        color: white;
                    }

                    tr:nth-child(even) {
                        background-color: #f2f2f2;
                    }

                    tr:hover {
                        background-color: #ddd;
                    }

                    /* Specific styles for individual tables */
                    .table-1x2, .table-3x4, .table-2x1 {
                        width: auto;
                    }

                    /* Styled link as button */
                    .link-button {
                        display: inline-block;
                        background-color: #0068AD;
                        color: white;
                        padding: 10px 20px;
                        text-align: center;
                        text-decoration: none;
                        font-size: 16px;
                        border-radius: 4px;
                        margin-top: 20px;
                    }

                     .link-button:hover {
                        background-color: #45a049;
                    }

                    .link-button::after {
                        content: "";
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        width: 100px; /* Adjust size as needed */
                        height: 100px; /* Adjust size as needed */
                        background-size: cover;
                        opacity: 0;
                        transition: opacity 0.3s ease;
                    }

                    .link-button:hover::after {
                        opacity: 1;
                    }

                    /* Title styling */
                    .title {
                        font-size: 24px;
                        font-weight: bold;
                        margin-bottom: 20px;
                    }
                </style>
            </head>"""
        html_content += f"""<body>
                  <div class="title">Employee Onboarding Checklist {'(' + self.name + ')'}</div>

                <!-- 3x4 Table -->
                <table class="table-3x4">
                    <thead>
                        <tr>
                            <th>Employee Type</th>
                            <th>Branch / Location</th>
                            <th colspan=2>Lateral Transfer</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>{self.dex_emp_type.title() if self.dex_emp_type else ''}</td>
                            <td>{self.branch_location.title() if self.branch_location else ''}</td>
                            <td colspan='2'>{'YES' if self.branch_location else 'NO'}</td>
                        </tr>
                    </tbody>
                    <thead>
                        <tr>
                            <th colspan="4">Employee Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Name</td>
                            <td>{self.emp_name.name.title() if self.emp_name else ''}</td>
                            <td>Gender</td>
                            <td>{self.birthday if self.birthday else ''}</td>
                        </tr>
                        <tr>
                            <td>Nickname</td>
                            <td>{self.login_name.title() if self.login_name else ''}</td>
                            <td>Employee ID</td>
                            <td>{self.emp_id if self.emp_id else ''}</td>
                        </tr>
                        <tr>
                            <td>Biometric ID</td>
                            <td>{self.bio_id if self.bio_id else ''}</td>
                            <td>Position</td>
                            <td>{self.job_id if self.job_id else ''}</td>
                        </tr>
                        <tr>
                            <td colspan="2">Onboard Date</td>
                            <td colspan="2">{self.onboard_date.strftime("%m-%d-%y") if self.onboard_date else ''}</td>
                        </tr>

                    </tbody>
                    <thead>
                        <tr>
                            <th colspan="4">Other Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Submitted By</td>
                            <td colspan="3">{self.requesters_id.name.title() if self.requesters_id else ''}</td>
                        </tr>
                        <tr>
                            <td>Submitted Date</td>
                            <td colspan="3">{self.submitted_date.strftime("%m-%d-%y") if self.submitted_date else ''}</td>
                        </tr>

                    </tbody>
                </table>

                {f'<a href="{self.generate_odoo_link()}" class="link-button">Edit Request Now</a>' if self.state == "ongoing" else ''}"""

        html_content += """</body>
            </html>

        """

        msg.attach(MIMEText(html_content, 'html'))

        try:
            smtpObj = smtplib.SMTP(host, port)
            smtpObj.login(username, password)
            smtpObj.sendmail(sender, get_all_email_receiver, msg.as_string())

            msg = "Successfully sent email"
            return {
                'success': {
                    'title': 'Successfully email sent!',
                    'message': f'{msg}'}
            }
        except Exception as e:
            msg = f"Error: Unable to send email: {str(e)}"
            return {
                'warning': {
                    'title': 'Error: Unable to send email!',
                    'message': f'{msg}'}
            }

    def approval_dashboard_link(self):
        # Approval Dashboard Link Section
        approval_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        approval_action = self.env['ir.actions.act_window'].search(
            [('name', '=', 'Onboarding Request Form')], limit=1)
        action_id = approval_action.id

        odoo_params = {
            "action": action_id,
        }

        query_string = '&'.join([f'{key}={value}' for key, value in odoo_params.items()])
        list_view_url = f"{approval_base_url}/web?debug=0#{query_string}"
        return list_view_url

    @api.depends('department_id', 'form_request_type')
    def _compute_approver_count(self):
        for record in self:
            department_approvers = self.env["approver.setup"].search([
                ("dept_name", "=", record.department_id.dept_name.name),
                ("approval_type", '=', record.form_request_type)
            ])
            count = sum(approver.no_of_approvers for approver in department_approvers)
            record.approver_count = count

    @api.onchange('department_id', 'approval_stage', 'form_request_type')
    def get_approver_domain(self):
        for rec in self:
            domain = []
            res = self.env["approver.setup"].search(
                [("dept_name", "=", rec.department_id.dept_name.name), ("approval_type", '=', self.form_request_type)])

            if rec.department_id and rec.approval_stage == 1:
                try:
                    approver_dept = [x.first_approver.id for x in res.set_first_approvers]
                    rec.approver_id = approver_dept[0]
                    domain.append(('id', '=', approver_dept))

                except IndexError:
                    raise UserError(_("No Approvers set for {}!").format(rec.department_id.dept_name.name))

            elif rec.department_id and rec.approval_stage == 2:
                approver_dept = [x.second_approver.id for x in res.set_second_approvers]
                rec.approver_id = approver_dept[0]
                domain.append(('id', '=', approver_dept))

            elif rec.department_id and rec.approval_stage == 3:
                approver_dept = [x.third_approver.id for x in res.set_third_approvers]
                rec.approver_id = approver_dept[0]
                domain.append(('id', '=', approver_dept))

            elif rec.department_id and rec.approval_stage == 4:
                approver_dept = [x.fourth_approver.id for x in res.set_fourth_approvers]
                rec.approver_id = approver_dept[0]
                domain.append(('id', '=', approver_dept))

            elif rec.department_id and rec.approval_stage == 5:
                approver_dept = [x.fifth_approver.id for x in res.set_fifth_approvers]
                rec.approver_id = approver_dept[0]
                domain.append(('id', '=', approver_dept))

            else:
                domain = []

            return {'domain': {'approver_id': domain}}

    @api.depends('current_user_groups1', 'requesters_id')
    def _compute_current_user_groups1(self):
        for record in self:
            user = self.env.user

            acl = self.env['ir.model.access'].search(
                [('model_id', '=', self.env.ref('dex_onboarding_checklist.model_employee_onboarding_checklist').id)])
            user_it = acl.filtered(lambda r: user.id in r.group_id.users.ids and r.group_id.name == 'IT')
            user_hr = acl.filtered(lambda r: user.id in r.group_id.users.ids and r.group_id.name == 'HR')

            if user_it.name == 'dex_onboarding_checklist.employee_onboarding_checklist_it':
                record.current_user_groups1 = 'it'
            elif user_hr.name == 'dex_onboarding_checklist.employee_onboarding_checklist_hr':
                record.current_user_groups1 = 'hr'
            else:
                record.current_user_groups1 = ''

    def generate_funny_intro(self, action, person, thing):
        intros = {
            "create": [
                f"🚨 HOLD ON! 🚨 {person} is about to unleash a tidal wave of new data on {thing}. It's going to be like opening a data firehose!",
                f"Attention: {person} is about to create data for {thing}. Expect a data explosion that might make your hard drive cry!",
                f"Warning: {person} is generating data for {thing}. The volume might be so overwhelming, even your coffee machine will be scared!",
                f"Get ready! {person} is about to flood {thing} with new data. It could be a data deluge or a full-on digital tsunami!",
                f"🚨 Emergency 🚨: {person} is about to turn {thing} into a data fiesta. Brace yourself for a party your server might not survive!",
                f"Prepare for a data bonanza! {person} is adding new entries to {thing}. It's going to be a confetti shower of information!",
                f"Alert: {person} is on a data creation spree with {thing}. If your system survives, it’ll have earned a medal for bravery!",
                f"🚨 Red Alert 🚨: {person} is about to drop a data bomb on {thing}. Hold onto your hats—it's going to be a wild ride!",
                f"Brace yourself! {person} is creating data for {thing}. The result might be so massive, you’ll need a bigger hard drive!",
                f"Warning: {person} is initiating data creation on {thing}. Expect so many entries, your spreadsheet might start sweating!",
                f"🚨 Critical Alert 🚨: {person} is unleashing new data on {thing}. Your system might request an early retirement!",
                f"Attention: {person} is generating data for {thing}. It’s going to be a digital fiesta your server will never forget!",
                f"Hold your breath! {person} is about to create data for {thing}. The volume might cause your computer to stage a protest!",
                f"🚨 Emergency 🚨: {person} is creating new data for {thing}. If your system survives, it deserves a standing ovation!",
                f"Prepare for impact! {person} is about to flood {thing} with new data. The sheer quantity might need its own zip code!"
            ],
            "delete": [
                f"🚨 WARNING 🚨: {person} is about to erase data from {thing}. Get ready for a data disaster that might make your backup cry!",
                f"Alert: {person} is removing data from {thing}. This could be a digital demolition derby—prepare for debris!",
                f"Warning: {person} is deleting data from {thing}. The fallout might be so dramatic, it could warrant a moment of silence!",
                f"Brace yourself! {person} is about to obliterate data from {thing}. It’s going to be a data vanishing act of epic proportions!",
                f"🚨 Red Alert 🚨: {person} is in the process of deleting data from {thing}. Prepare for a potential data meltdown that might make headlines!",
                f"Attention: {person} is about to wipe out data from {thing}. The results might be so catastrophic, even your system will need therapy!",
                f"Disaster Incoming: {person} is removing data from {thing}. Brace for a data apocalypse that could rival the end of days!",
                f"Warning: {person} is executing a data deletion on {thing}. The aftermath might be a dramatic void your system will never forget!",
                f"🚨 Critical Alert 🚨: {person} is about to delete {thing}. The results might be so epic, they could inspire a new disaster movie!",
                f"Hold on tight! {person} is removing data from {thing}. The fallout could be so massive, even your cloud storage might panic!",
                f"Attention: {person} is about to erase data from {thing}. The chaos could be so profound, it might require an emergency data recovery plan!",
                f"Brace for impact! {person} is deleting data from {thing}. The result might be so dramatic, it’ll make your system question its existence!",
                f"🚨 Emergency 🚨: {person} is in the process of wiping out data from {thing}. Expect a data meltdown that’ll be the talk of the tech town!",
                f"Warning: {person} is about to obliterate data from {thing}. Prepare for a data vacuum that might create a black hole in your system!",
                f"Disaster Alert: {person} is about to erase {thing}. The results might be so epic, your server might demand a vacation!"
            ],
            "edit": [
                f"🚨 ALERT 🚨: {person} is about to edit data in {thing}. Hold on—these changes might turn your data into a circus act!",
                f"Attention: {person} is making edits to {thing}. Expect changes so wild, they could make your spreadsheet do the cha-cha!",
                f"Warning: {person} is modifying data in {thing}. Brace for an overhaul so extreme, it might require a data intervention!",
                f"Get ready! {person} is about to alter data in {thing}. The result could be a chaotic transformation that’ll have your data in therapy!",
                f"🚨 Emergency 🚨: {person} is making changes to {thing}. The edits might be so dramatic, they’ll make reality TV look boring!",
                f"Brace yourself! {person} is editing data in {thing}. Expect a rollercoaster of changes that might turn your data upside down!",
                f"Attention: {person} is about to edit {thing}. The modifications might be so outlandish, they’ll require a data rescue mission!",
                f"Warning: {person} is making changes to {thing}. Prepare for a potential data shake-up that could be the next big tech scandal!",
                f"🚨 Red Alert 🚨: {person} is about to edit {thing}. The alterations might be so epic, they’ll be talked about in data circles for years!",
                f"Hold your breath! {person} is about to make changes to {thing}. The result could be a data transformation that’ll go viral!",
                f"Disaster Incoming: {person} is editing data in {thing}. The changes might be so significant, even your backups will need therapy!",
                f"Attention: {person} is making edits to {thing}. The outcome could be so dramatic, it might lead to a new data revolution!",
                f"Brace for impact! {person} is altering data in {thing}. The changes might be so extreme, they’ll make your data history!",
                f"🚨 Critical Alert 🚨: {person} is about to edit {thing}. Expect changes so dramatic, they might need their own reality show!",
                f"Warning: {person} is making edits to {thing}. The modifications might be so grand, your data will need a recovery team!"
            ]
        }

        return random.choice(intros[action])

    def _notify_email(self, get_all_email_receiver, person, action):
        conn = self.main_connection()
        sender = 'HEY IT PEEPS!.'
        host = conn['host']
        port = conn['port']
        username = conn['username']
        password = conn['password']

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        token = self.generate_token()

        approval_url = "{}/dex_onboarding_checklist/request/cpp_approve/{}".format(base_url, token)
        disapproval_url = "{}/dex_onboarding_checklist/request/cpp_disapprove/{}".format(base_url, token)

        thing = f'<a href="{self.generate_odoo_link()}" class="link-button">{self.name}</a>'

        self.with_context({'no_log': True}).write({'approval_link': token})
        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))

        msg['To'] = ', '.join(get_all_email_receiver)
        msg[
            'Subject'] = f"SOMEONE EDITED THIS [{self.name}]"

        html_content = f"""
                    <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Multiple Tables</title>
            </head>
            <body>
                  <div class="title">{self.generate_funny_intro(action, person, thing)}</div>
            
            
            </body>
            </html>
        """

        msg.attach(MIMEText(html_content, 'html'))

        try:
            smtpObj = smtplib.SMTP(host, port)
            smtpObj.login(username, password)
            smtpObj.sendmail(sender, get_all_email_receiver, msg.as_string())

            msg = "Successfully sent email"
            return {
                'success': {
                    'title': 'Successfully email sent!',
                    'message': f'{msg}'}
            }
        except Exception as e:
            msg = f"Error: Unable to send email: {str(e)}"
            return {
                'warning': {
                    'title': 'Error: Unable to send email!',
                    'message': f'{msg}'}
            }

    # # Example usage
    # person = "Alice"
    # thing = "the database"
    #
    # # For creating data
    # print("Creating Data:")
    # for _ in range(3):
    #     print(generate_funny_intro("create", person, thing))
    #
    # # For deleting data
    # print("\nDeleting Data:")
    # for _ in range(3):
    #     print(generate_funny_intro("delete", person, thing))
    #
    # # For editing data
    # print("\nEditing Data:")
    # for _ in range(3):
    #     print(generate_funny_intro("edit", person, thing))
