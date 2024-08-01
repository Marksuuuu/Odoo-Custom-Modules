import datetime
import hashlib
import re
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import formataddr

import logging

_logger = logging.getLogger(__name__)


class TransportNetworkVehicleForm(models.Model):
    _name = 'transport.network.vehicle.form'
    _inherit = ['approval.fields.plugins', 'abstract.function']

    tnvf_ids = fields.One2many('transport.network.vehicle.form.line', 'tnvf_lines', string='Line Ids')
    approver_id = fields.Many2one('hr.employee', string="Approver", domain=lambda self: self.get_approver_domain(),
                                  store=True)
    check_status = fields.Char(compute='compute_check_status', store=True)

    approver_count = fields.Integer(compute='_compute_approver_count', store=True)

    approved_by = fields.Many2one('res.users', string="Approved By")
    date_approved = fields.Datetime()

    is_approver = fields.Boolean(compute="compute_approver")

    transport_vehicle_type = fields.Many2one('transport.network.vehicle.type', string='Transport Vehicle Type')

    transport_vehicle_type_rate = fields.Float(string='Transport Vehicle Rate')

    total_rate = fields.Float(string="Total", compute="_compute_tnvf_amount", store=True)

    cargo_type = fields.Selection([
        ('personnel', 'Personnel'),
        ('package', 'Package')], default='personnel')

    parameter_match = fields.Boolean(string="Parameter Match", compute='_compute_parameter_match', store=False,
                                     readonly=False,
                                     default=False)
    flag_counter = fields.Boolean(default=False)

    is_bill_created = fields.Many2one('account.move', tracking=True, string="Bill Created")

    person_who_billed = fields.Many2one('res.users', string='Person Who Billed')

    is_created_bill = fields.Boolean(default=False, tracking=True)

    get_status_for_bill = fields.Selection(related='is_bill_created.state')

    @api.depends('department_id', 'department_id.requests_handlers', 'flag_counter')
    def _compute_parameter_match(self):
        for record in self:
            # Retrieve the configuration parameter value
            user_record = record.department_id

            # Accessing the courses of the department
            courses = user_record.requests_handlers

            # Initialize parameter_match to False
            parameter_match = False

            # Get current user data
            current_user = self.env.user

            # Iterating through the courses
            for course in courses:
                # Compare parameter value with current user's id
                if int(course.id) == int(current_user.id):
                    parameter_match = True
                    record.flag_counter = True  # You may want to set flag_counter to True here as well
                    break  # No need to continue if match is found

            # Update the parameter_match field
            record.parameter_match = parameter_match

    @api.depends('department_id.is_need_request_handlers')
    def checking_if_need_request_are_true(self):
        for rec in self:
            if rec.department_id.is_need_request_handlers:
                rec.send_to_purchase_rep(self.get_purchase_rep_email())
            else:
                print('else')
                pass

    def check_get_purchase_rep_email(self):
        self.checking_if_need_request_are_true()

    def get_purchase_rep_email(self):
        work_emails = []  # Initialize an empty list to store work emails
        for record in self:
            # Assuming record is related to a student or contains necessary information
            # to find the related student record

            # Retrieve the student record or department record
            student_record = record.department_id  # Replace department_id with the appropriate field

            # Assuming requests_handlers is a one-to-many or many-to-many field on the student record
            courses = student_record.requests_handlers  # Accessing the courses of the student

            # Assuming user_id is a field on hr.employee model
            search_for_users = self.env['hr.employee'].search([('user_id', 'in', courses.mapped('id'))])

            # Loop through all matching HR employees and append their work emails to the list
            for user in search_for_users:
                work_emails.append(user.work_email)

        # Return the list of work emails
        print(work_emails)
        return work_emails

    @api.depends('tnvf_ids', 'total_rate')
    def _compute_tnvf_amount(self):
        for record in self:
            estimated_tnvf_amount = [line.tnvf_amount for line in record.tnvf_ids]
            total_tnvf_amount = sum(estimated_tnvf_amount)
            record.total_rate = sum(estimated_tnvf_amount)

    def submit_to_final_approver(self):
        all_list = self.get_approvers_in_list()
        email_list = [self.initial_approver_email, self.second_approver_email,
                      self.third_approver_email, self.fourth_approver_email,
                      self.final_approver_email, self.requesters_email]

        recipient_list = [email for email in email_list if email]

        # Remove duplicates from recipient_list
        recipient_list = list(set(recipient_list + all_list))  # Combine and then create set
        print(recipient_list)
        if recipient_list:
            self.send_to_final_approver_email(recipient_list)
        else:
            print("No valid email addresses found.")

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

    def send_to_final_approver_email(self, recipient_list):
        conn = self.main_connection()
        sender = conn['sender']
        host = conn['host']
        port = conn['port']
        username = conn['username']
        password = conn['password']

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        token = self.generate_token()

        approval_url = "{}/dex_form_request_approval/request/tnvf_approve/{}".format(base_url, token)
        disapproval_url = "{}/dex_form_request_approval/request/tnvf_disapprove/{}".format(base_url, token)

        token = self.generate_token()
        self.write({'approval_link': token})

        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))

        msg['To'] = ', '.join(recipient_list)
        msg[
            'Subject'] = f"{re.sub(r'[-_]', ' ', self.form_request_type).title() if self.approval_status else ''} Request has been [{re.sub(r'[-_]', ' ', self.approval_status).title() if self.approval_status else ''}] [{self.name}]"

        html_content = """
                    <!DOCTYPE html>
                        <html lang="en">
                        <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Invoice Template</title>
                        <style>
                            body {
                                font-family: Arial, sans-serif;
                                margin: 0;
                                padding: 20px;
                            }
                            .container {
                                max-width: 800px;
                                margin: 0 auto;
                                border: 1px solid #ccc;
                                padding: 20px;
                                position: relative;
                            }
                            .header {
                                text-align: center;
                                margin-bottom: 20px;
                            }
                            .invoice-number {
                                position: absolute;
                                top: 20px;
                                right: 20px;
                            }
                            table {
                                width: 100%;
                                border-collapse: collapse;
                                margin-top: 20px;
                            }
                            th, td {
                                border: 1px solid #ddd;
                                padding: 8px;
                                text-align: left;
                            }
                            th {
                                background-color: #f2f2f2;
                            }
                            .button-container {
                                text-align: center;
                                margin-top: 20px;
                            }
                            .button {
                                padding: 10px 20px;
                                margin: 0 10px;
                                border: none;
                                border-radius: 5px;
                                cursor: pointer;
                                font-size: 16px;
                                color: white;
                                transition: background-color 0.3s;
                            }
                            .button:hover {
                                background-color: grey;
                            }
                        </style>
                        </head>
                        <body> """

        html_content += f""" 
                            <div class="container">
                                <div class="header">
                                    <h2>{re.sub(r'[-_]', ' ', self.form_request_type).title() if self.approval_status else ''} Request</h2>
                                    <p>Date: {self.create_date.strftime("%m-%d-%y")}</p>
                                    <p>Request by: {self.requesters_id.name}</p>
                                </div>
                                <div class="invoice-number" style='text-align: center'>
                                    <p>Serial Number: </br> {self.name}</p>
                                </div>
                                <div class="item-details">
                                    <h3>Item Details</h3>
                                    <p>Status: {'To Approve' if self.approval_status == 'draft' else re.sub(r'[-_]', ' ', self.approval_status).title()}</p>
                                    <p>Item Requested: {re.sub(r'[-_]', ' ', self.form_request_type).title() if self.approval_status else ''}</p>
                                    <p>Approved by: {self.env.user.name if self.env.user else ''}</p>
                                    <p>Transport Vehicle: {self.transport_vehicle_type.tnv_type if self.transport_vehicle_type else ''}</p>
                                    <p>Cargo Type: {self.cargo_type if self.cargo_type else ''}</p>
                                </div>"""

        html_content += """
                                                                        <table>
                                                                            <thead>
                                                                                <tr>
                                                                                    <th>Personnel</th>
                                                                                    <th>Package</th>
                                                                                    <th>From</th>
                                                                                    <th>To</th>
                                                                                    <th>Rate</th>
                                                                                    <th>Purpose</th>
                                                                                </tr>
                                                                            </thead>
                                                                            <tbody>
                                                                            """
        for rec in self.tnvf_ids:
            html_content += f"""

                                                                  <tr>
                                                                            <td>{rec.tnvf_personnel if rec.tnvf_personnel else ''}</td>
                                                                            <td>{rec.tnvf_package if rec.tnvf_package else ''}</td>
                                                                            <td>{rec.tnvf_from if rec.tnvf_from else ''}</td>
                                                                            <td>{rec.tnvf_to if rec.tnvf_to else ''}</td>
                                                                            <td>{rec.tnvf_amount if rec.tnvf_amount else ''}</td>
                                                                            <td>{rec.tnvf_purpose if rec.tnvf_purpose else ''}</td>
                                                                  </tr>

                                                            """
        html_content += f"""
        </tbody> 
                                                                        </table>
                                                        <div class="button-container">
                                                            <p>Total Rate: {self.total_rate}</p>
                                                        </div>"""

        html_content += f"""

                                <div class="button-container">
                                    <a href="{self.generate_odoo_link()}" style="background-color: blue; margin-right: 20px; margin-top: 20px;" class="button">Dashboard</a>
                                </div>"""

        html_content += """
                        </body>
                        </html>
                """

        msg.attach(MIMEText(html_content, 'html'))

        try:
            smtpObj = smtplib.SMTP(host, port)
            smtpObj.login(username, password)
            smtpObj.sendmail(sender, recipient_list, msg.as_string())

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

    @api.depends('approval_stage')
    def approve_request(self):
        for rec in self:

            res = self.env["approver.setup"].search([
                ("dept_name", "=", rec.department_id.dept_name.name),
                ("approval_type", '=', rec.form_request_type)
            ])

            if rec.approval_status == 'to_approve':
                print('approval status: ', rec.approval_status)
                if rec.approver_id and rec.approval_stage < res.no_of_approvers:
                    if rec.approval_stage == 1:

                        if self.initial_approver_name is None:
                            raise UserError('No approver set')
                        else:
                            self.initial_approver_name = rec.approver_id.name

                        approver_dept = [x.second_approver.id for x in res.set_second_approvers]

                        self.write({
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
                            self.second_approver_name = rec.approver_id.name
                        approver_dept = [x.third_approver.id for x in res.set_third_approvers]

                        self.write({
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
                            self.third_approver_name = rec.approver_id.name

                        approver_dept = [x.fourth_approver.id for x in res.set_fourth_approvers]

                        self.write({
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
                            self.fourth_approver_name = rec.approver_id.name

                        approver_dept = [x.fifth_approver.id for x in res.set_fifth_approvers]

                        self.write({
                            'approver_id': approver_dept[0]
                        })

                        recipient_list = []
                        if self.department_id and self.department_id.set_fifth_approvers:
                            for approver in self.department_id.set_fifth_approvers:
                                if approver.approver_email:
                                    recipient_list.append(approver.approver_email)

                        self.submit_to_next_approver(recipient_list)
                        self.save_current_date()

                    rec.approval_stage += 1
                else:
                    self.write({
                        'approval_status': 'approved',
                        'state': 'approved',
                        'final_approver_name': rec.approver_id.name,
                        'approval_link': ''
                    })
                    self.save_current_date()
            else:
                print('approval status else: ', rec.approval_status)

    def submit_to_next_approver(self, approver_to_send):
        # Approval Dashboard Link Section

        approval_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        approval_action = self.env['ir.actions.act_window'].search(
            [('name', '=', 'Transport Network Vehicle')], limit=1)
        action_id = approval_action.id
        odoo_params = {
            "action": action_id,
        }

        query_string = '&'.join([f'{key}={value}' for key, value in odoo_params.items()])
        approval_list_view_url = f"{approval_base_url}/web?debug=0#{query_string}"

        # Generate Odoo Link Section
        odoo_action = self.env['ir.actions.act_window'].search([('res_model', '=', 'transport.network.vehicle.form')],
                                                               limit=1)
        odoo_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        odoo_result = re.sub(r'\((.*?)\)', '', str(odoo_action)).replace(',', '')
        odoo_res = f"{odoo_result},{odoo_action.id}"
        odoo_result = re.sub(r'\s*,\s*', ',', odoo_res)

        odoo_menu = self.env['ir.ui.menu'].search([('action', '=', odoo_result)], limit=1)
        odoo_params = {
            "id": self.id,
            "action": odoo_action.id,
            "model": "transport.network.vehicle.form",
            "view_type": "form",
            "cids": 1,
            "menu_id": odoo_menu.id
        }
        odoo_query_params = "&".join(f"{key}={value}" for key, value in odoo_params.items())
        form_link = f"{odoo_base_url}/web#{odoo_query_params}"

        self.generate_odoo_link()
        self.approval_dashboard_link()

        get_all_email_receiver = self.approver_id.work_email  # <-- This Code are for One approver set only
        self.sending_email_to_next_approver(approver_to_send, form_link, approval_list_view_url)

        self.write({
            'approval_status': 'to_approve',
            'state': 'to_approve',
        })

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

    def sending_email_to_next_approver(self, get_all_email_receiver, form_link, approval_list_view_url):
        conn = self.main_connection()
        sender = conn['sender']
        host = conn['host']
        port = conn['port']
        username = conn['username']
        password = conn['password']

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        token = self.generate_token()

        approval_url = "{}/dex_form_request_approval/request/tnvf_approve/{}".format(base_url, token)
        disapproval_url = "{}/dex_form_request_approval/request/tnvf_disapprove/{}".format(base_url, token)

        self.write({'approval_link': token})
        print(self.approval_link)
        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))
        msg['To'] = ', '.join(get_all_email_receiver)
        msg[
            'Subject'] = f"{re.sub(r'[-_]', ' ', self.form_request_type).title() if self.approval_status else ''} Request for Approval [{self.name}]"

        html_content = """
                    <!DOCTYPE html>
                        <html lang="en">
                        <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Invoice Template</title>
                        <style>
                            body {
                                font-family: Arial, sans-serif;
                                margin: 0;
                                padding: 20px;
                            }
                            .container {
                                max-width: 800px;
                                margin: 0 auto;
                                border: 1px solid #ccc;
                                padding: 20px;
                                position: relative;
                            }
                            .header {
                                text-align: center;
                                margin-bottom: 20px;
                            }
                            .invoice-number {
                                position: absolute;
                                top: 20px;
                                right: 20px;
                            }
                            table {
                                width: 100%;
                                border-collapse: collapse;
                                margin-top: 20px;
                            }
                            th, td {
                                border: 1px solid #ddd;
                                padding: 8px;
                                text-align: left;
                            }
                            th {
                                background-color: #f2f2f2;
                            }
                            .button-container {
                                text-align: center;
                                margin-top: 20px;
                            }
                            .button {
                                padding: 10px 20px;
                                margin: 0 10px;
                                border: none;
                                border-radius: 5px;
                                cursor: pointer;
                                font-size: 16px;
                                color: white;
                                transition: background-color 0.3s;
                            }
                            .button:hover {
                                background-color: grey;
                            }
                        </style>
                        </head>
                        <body> """

        html_content += f""" 
                            <div class="container">
                                <div class="header">
                                    <h2>{re.sub(r'[-_]', ' ', self.form_request_type).title() if self.approval_status else ''} Request</h2>
                                    <p>Date: {self.create_date.strftime("%m-%d-%y")}</p>
                                    <p>Request by: {self.requesters_id.name}</p>
                                </div>
                                <div class="invoice-number" style='text-align: center'>
                                    <p>Serial Number: </br> {self.name}</p>
                                </div>
                                <div class="item-details">
                                    <h3>Item Details</h3>
                                    <p>Status: {'To Approve' if self.approval_status == 'draft' else re.sub(r'[-_]', ' ', self.approval_status).title()}</p>
                                    <p>Item Requested: {re.sub(r'[-_]', ' ', self.form_request_type).title() if self.approval_status else ''}</p>
                                    <p>Approved by: {self.env.user.name if self.env.user else ''}</p>
                                    <p>Transport Vehicle: {self.transport_vehicle_type.tnv_type if self.transport_vehicle_type else ''}</p>
                                    <p>Cargo Type: {self.cargo_type if self.cargo_type else ''}</p>
                                </div>"""

        html_content += """
                                                                <table>
                                                                    <thead>
                                                                        <tr>
                                                                            <th>Personnel</th>
                                                                            <th>Package</th>
                                                                            <th>From</th>
                                                                            <th>To</th>
                                                                            <th>Rate</th>
                                                                            <th>Purpose</th>
                                                                        </tr>
                                                                    </thead>
                                                                    <tbody>
                                                                    """
        for rec in self.tnvf_ids:
            html_content += f"""

                                                                  <tr>
                                                                            <td>{rec.tnvf_personnel if rec.tnvf_personnel else ''}</td>
                                                                            <td>{rec.tnvf_package if rec.tnvf_package else ''}</td>
                                                                            <td>{rec.tnvf_from if rec.tnvf_from else ''}</td>
                                                                            <td>{rec.tnvf_to if rec.tnvf_to else ''}</td>
                                                                            <td>{rec.tnvf_amount if rec.tnvf_amount else ''}</td>
                                                                            <td>{rec.tnvf_purpose if rec.tnvf_purpose else ''}</td>
                                                                  </tr>

                                                            """
        html_content += f"""
        </tbody> 
                                                                        </table>
                                                        <div class="button-container">
                                                            <p>Total Rate: {self.total_rate}</p>
                                                        </div>"""

        html_content += f"""

                                <div class="button-container">
                                    <a href='{approval_url}' style="background-color: green; margin-right: 20px; margin-top: 20px;" class="button">Approve</a>
                                    <a href='{disapproval_url}' style="background-color: red; margin-right: 20px; margin-top: 20px;" class="button">Disapprove</a>
                                    <a href="{self.generate_odoo_link()}" style="background-color: blue; margin-right: 20px; margin-top: 20px;" class="button">Dashboard</a>
                                </div>"""

        html_content += """
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

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('create.sequence.form.sequence.tnv') or '/'
        return super(TransportNetworkVehicleForm, self).create(vals)

    def _get_department_domain(self):
        approval_types = self.env['approver.setup'].search([('approval_type', '=', 'transport_network_vehicle')])
        return [('id', 'in', approval_types.ids)]

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

    @api.depends('department_id', 'form_request_type')
    def _compute_approver_count(self):
        for record in self:
            department_approvers = self.env["approver.setup"].search([
                ("dept_name", "=", record.department_id.dept_name.name),
                ("approval_type", '=', record.form_request_type)
            ])
            count = sum(approver.no_of_approvers for approver in department_approvers)
            record.approver_count = count

    @api.depends('approval_status')
    def compute_check_status(self):
        for rec in self:
            if rec.approval_status == 'approved':
                rec.get_approvers_email()
                rec.submit_to_final_approver()
                rec.checking_if_need_request_are_true()
            elif rec.approval_status == 'disapprove':
                rec.get_approvers_email()
                rec.submit_for_disapproval()

    def send_to_purchase_rep(self, recipient_list):
        conn = self.main_connection()
        print(recipient_list)
        sender = conn['sender']
        host = conn['host']
        port = conn['port']
        username = conn['username']
        password = conn['password']

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        token = self.generate_token()

        approval_url = "{}/dex_form_request_approval/request/cpp_approve/{}".format(base_url, token)
        disapproval_url = "{}/dex_form_request_approval/request/cpp_disapprove/{}".format(base_url, token)

        token = self.generate_token()
        self.write({'approval_link': token})

        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))

        msg['To'] = ', '.join(recipient_list)
        msg[
            'Subject'] = f"{re.sub(r'[-_]', ' ', self.form_request_type).title() if self.approval_status else ''} Request has been {re.sub(r'[-_]', ' ', self.approval_status).title() if self.approval_status else ''} [{self.name}], Please Process"
        html_content = """
                                    <!DOCTYPE html>
                                        <html lang="en">
                                        <head>
                                        <meta charset="UTF-8">
                                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                        <title>Invoice Template</title>
                                        <style>
                                            body {
                                                font-family: Arial, sans-serif;
                                                margin: 0;
                                                padding: 20px;
                                            }
                                            .container {
                                                max-width: 800px;
                                                margin: 0 auto;
                                                border: 1px solid #ccc;
                                                padding: 20px;
                                                position: relative;
                                            }
                                            .header {
                                                text-align: center;
                                                margin-bottom: 20px;
                                            }
                                            .invoice-number {
                                                position: absolute;
                                                top: 20px;
                                                right: 20px;
                                            }
                                            table {
                                                width: 100%;
                                                border-collapse: collapse;
                                                margin-top: 20px;
                                            }
                                            th, td {
                                                border: 1px solid #ddd;
                                                padding: 8px;
                                                text-align: left;
                                            }
                                            th {
                                                background-color: #f2f2f2;
                                            }
                                            .button-container {
                                                text-align: center;
                                                margin-top: 20px;
                                            }
                                            .button {
                                                padding: 10px 20px;
                                                margin: 0 10px;
                                                border: none;
                                                border-radius: 5px;
                                                cursor: pointer;
                                                font-size: 16px;
                                                color: white;
                                                transition: background-color 0.3s;
                                            }
                                            .button:hover {
                                                background-color: grey;
                                            }
                                            /* Apply ellipsis to links */
                                            td.website-link {
                                                max-width: 50px; /* Adjust the maximum width as needed */
                                                overflow: hidden;
                                                text-overflow: ellipsis;
                                                white-space: nowrap;
                                            }

                                        </style>
                                        </head>
                                        <body> """

        html_content += f""" 
                                            <div class="container">
                                                <div class="header">
                                                    <h2>{re.sub(r'[-_]', ' ', self.form_request_type).title() if self.approval_status else ''} Request</h2>
                                                    <p>Date: {self.create_date.strftime("%m-%d-%y")}</p>
                                                    <p>Request by: {self.requesters_id.name}</p>
                                                </div>
                                                <div class="invoice-number" style='text-align: center'>
                                                    <p>Serial Number: </br> {self.name}</p>
                                                </div>
                                                <div class="item-details">
                                                    <h3>Item Details</h3>
                                                    <p>Status: {'To Approve' if self.approval_status == 'draft' else re.sub(r'[-_]', ' ', self.approval_status).title()}</p>
                                                    <p>Item Requested: {re.sub(r'[-_]', ' ', self.form_request_type).title() if self.approval_status else ''}</p>
                                                    <p>{re.sub(r'[-_]', ' ', self.approval_status).title() if self.approval_status else '' if self.approval_status == 'approved' else ''} by: {self.env.user.name if self.env.user else ''}</p>
                                                </div>"""

        html_content += """
                                                        <table>
                                                            <thead>
                                                                <tr>
                                                                    <th>Personnel</th>
                                                                    <th>Package</th>
                                                                    <th>From</th>
                                                                    <th>To</th>
                                                                    <th>Rate</th>
                                                                    <th>Purpose</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                                            """
        for rec in self.tnvf_ids:
            html_content += f"""

                                                                          <tr>
                                                                                    <td>{rec.tnvf_personnel if rec.tnvf_personnel else ''}</td>
                                                                                    <td>{rec.tnvf_package if rec.tnvf_package else ''}</td>
                                                                                    <td>{rec.tnvf_from if rec.tnvf_from else ''}</td>
                                                                                    <td>{rec.tnvf_to if rec.tnvf_to else ''}</td>
                                                                                    <td>{rec.tnvf_amount if rec.tnvf_amount else ''}</td>
                                                                                    <td>{rec.tnvf_purpose if rec.tnvf_purpose else ''}</td>
                                                                          </tr>

                                                                    """
        html_content += f"""
                                                            </tbody> 
                                                            </table>
                                                                <div class="button-container">
                                                                    <p>Total Rate: {self.total_rate}</p>
                                                                </div>"""
        html_content += f"""
                                                <div class="button-container">
                                                            <a href="{self.generate_odoo_link()}" style="background-color: blue; margin-right: 20px; margin-top: 20px;" class="button">Edit Now</a>
                                                </div>"""

        html_content += """
                                            </div>
                                        </body>
                                        </html>
                                """

        msg.attach(MIMEText(html_content, 'html'))

        try:
            smtpObj = smtplib.SMTP(host, port)
            smtpObj.login(username, password)
            smtpObj.sendmail(sender, recipient_list, msg.as_string())

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

    @api.depends('approval_status')
    def get_approvers_email(self):
        """
        Retrieves the email addresses of the relevant approvers based on approval status and approval_stock_state.

        Side Effects:
            Updates the email fields of the instance with the appropriate approver emails.
        """
        for rec in self:
            if rec.approval_status == 'approved':
                if rec.initial_approver_name:
                    approver = self.env['hr.employee'].search([('name', '=', rec.initial_approver_name)],
                                                              limit=1)
                    rec.initial_approver_email = approver.work_email if approver else False

                if rec.second_approver_name:
                    approver = self.env['hr.employee'].search([('name', '=', rec.second_approver_name)], limit=1)
                    rec.second_approver_email = approver.work_email if approver else False

                if rec.third_approver_name:
                    approver = self.env['hr.employee'].search([('name', '=', rec.third_approver_name)], limit=1)
                    rec.third_approver_email = approver.work_email if approver else False

                if rec.fourth_approver_name:
                    approver = self.env['hr.employee'].search([('name', '=', rec.fourth_approver_name)], limit=1)
                    rec.fourth_approver_email = approver.work_email if approver else False

                if rec.final_approver_name:
                    approver = self.env['hr.employee'].search([('name', '=', rec.final_approver_name)], limit=1)
                    rec.final_approver_email = approver.work_email if approver else False

                rec.requesters_email = self.requesters_email

            elif rec.approval_status == 'disapprove':
                res = self.env["approver.setup"].search(
                    [("dept_name", "=", rec.department_id.dept_name.name),
                     ("approval_type", '=', self.form_request_type)])

                initial_approver_email = False
                second_approver_email = False
                third_approver_email = False
                fourth_approver_email = False
                final_approver_email = False

                if rec.department_id and res.set_first_approvers:
                    initial_approver_email = res.set_first_approvers[0].first_approver.work_email

                if rec.department_id and res.set_second_approvers:
                    second_approver_email = res.set_second_approvers[0].second_approver.work_email

                if rec.department_id and res.set_third_approvers:
                    third_approver_email = res.set_third_approvers[0].third_approver.work_email

                if rec.department_id and res.set_fourth_approvers:
                    fourth_approver_email = res.set_fourth_approvers[0].fourth_approver.work_email

                if rec.department_id and res.set_fifth_approvers:
                    final_approver_email = res.set_fifth_approvers[0].fifth_approver.work_email

                rec.initial_approver_email = initial_approver_email
                rec.second_approver_email = second_approver_email
                rec.third_approver_email = third_approver_email
                rec.fourth_approver_email = fourth_approver_email
                rec.final_approver_email = final_approver_email

                rec.requesters_email = self.requesters_email

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

    def submit_for_approval(self):
        # Approval Dashboard Link Section
        approval_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        approval_action = self.env['ir.actions.act_window'].search(
            [('name', '=', 'Transport Network Vehicle')], limit=1)
        action_id = approval_action.id

        odoo_params = {
            "action": action_id,
        }

        query_string = '&'.join([f'{key}={value}' for key, value in odoo_params.items()])
        approval_list_view_url = f"{approval_base_url}/web?debug=0#{query_string}"

        # Generate Odoo Link Section
        odoo_action = self.env['ir.actions.act_window'].search([('res_model', '=', 'transport.network.vehicle.form')],
                                                               limit=1)
        odoo_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        odoo_result = re.sub(r'\((.*?)\)', '', str(odoo_action)).replace(',', '')
        odoo_res = f"{odoo_result},{odoo_action.id}"
        odoo_result = re.sub(r'\s*,\s*', ',', odoo_res)

        odoo_menu = self.env['ir.ui.menu'].search([('action', '=', odoo_result)], limit=1)
        odoo_params = {
            "id": self.id,
            "action": odoo_action.id,
            "model": "transport.network.vehicle.form",
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

        self.write({
            'approval_status': 'to_approve',
            'state': 'to_approve',
        })

    def generate_token(self):
        now = datetime.now()
        token = "{}-{}-{}-{}".format(self.id, self.name, self.env.user.id, now)
        return hashlib.sha256(token.encode()).hexdigest()

    def generate_odoo_link(self):
        # Generate Odoo Link Section
        action = self.env['ir.actions.act_window'].search([('res_model', '=', 'transport.network.vehicle.form')],
                                                          limit=1)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        result = re.sub(r'\((.*?)\)', '', str(action)).replace(',', '')
        res = f"{result},{action.id}"
        result = re.sub(r'\s*,\s*', ',', res)

        menu = self.env['ir.ui.menu'].search([('action', '=', result)], limit=1)
        params = {
            "id": self.id,
            "action": action.id,
            "model": "transport.network.vehicle.form",
            "view_type": "form",
            "cids": 1,
            "menu_id": menu.id
        }
        query_params = "&".join(f"{key}={value}" for key, value in params.items())
        form_link = f"{base_url}/web#{query_params}"
        return form_link

    def sending_email(self, get_all_email_receiver, form_link, approval_list_view_url):
        conn = self.main_connection()
        sender = conn['sender']
        host = conn['host']
        port = conn['port']
        username = conn['username']
        password = conn['password']

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        token = self.generate_token()

        approval_url = "{}/dex_form_request_approval/request/tnvf_approve/{}".format(base_url, token)
        disapproval_url = "{}/dex_form_request_approval/request/tnvf_disapprove/{}".format(base_url, token)

        self.write({'approval_link': token})
        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))
        msg['To'] = ', '.join(get_all_email_receiver)
        msg[
            'Subject'] = f"{re.sub(r'[-_]', ' ', self.form_request_type).title() if self.approval_status else ''} Request for Approval [{self.name}]"

        html_content = """
            <!DOCTYPE html>
                <html lang="en">
                <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Invoice Template</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                        border: 1px solid #ccc;
                        padding: 20px;
                        position: relative;
                    }
                    .header {
                        text-align: center;
                        margin-bottom: 20px;
                    }
                    .invoice-number {
                        position: absolute;
                        top: 20px;
                        right: 20px;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }
                    th, td {
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }
                    th {
                        background-color: #f2f2f2;
                    }
                    .button-container {
                        text-align: center;
                        margin-top: 20px;
                    }
                    .button {
                        padding: 10px 20px;
                        margin: 0 10px;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 16px;
                        color: white;
                        transition: background-color 0.3s;
                    }
                    .button:hover {
                        background-color: grey;
                    }
                </style>
                </head>
                <body> """

        html_content += f""" 
                    <div class="container">
                        <div class="header">
                            <h2>{re.sub(r'[-_]', ' ', self.form_request_type).title() if self.approval_status else ''} Request</h2>
                            <p>Date: {self.create_date.strftime("%m-%d-%y")}</p>
                            <p>Request by: {self.requesters_id.name}</p>
                        </div>
                        <div class="invoice-number" style='text-align: center'>
                            <p>Serial Number: </br> {self.name}</p>
                        </div>
                                <div class="item-details">
                                    <h3>Item Details</h3>
                                    <p>Status: {'To Approve' if self.approval_status == 'draft' else re.sub(r'[-_]', ' ', self.approval_status).title()}</p>
                                    <p>Item Requested: {re.sub(r'[-_]', ' ', self.form_request_type).title() if self.approval_status else ''}</p>
                                    <p>Approved by: {self.env.user.name if self.env.user else ''}</p>
                                    <p>Transport Vehicle: {self.transport_vehicle_type.tnv_type if self.transport_vehicle_type else ''}</p>
                                    <p>Cargo Type: {self.cargo_type if self.cargo_type else ''}</p>
                                </div>"""

        html_content += """
                                                        <table>
                                                            <thead>
                                                                <tr>
                                                                    <th>Personnel</th>
                                                                    <th>Package</th>
                                                                    <th>From</th>
                                                                    <th>To</th>
                                                                    <th>Rate</th>
                                                                    <th>Purpose</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                                            """
        for rec in self.tnvf_ids:
            html_content += f"""

                                                                  <tr>
                                                                            <td>{rec.tnvf_personnel if rec.tnvf_personnel else ''}</td>
                                                                            <td>{rec.tnvf_package if rec.tnvf_package else ''}</td>
                                                                            <td>{rec.tnvf_from if rec.tnvf_from else ''}</td>
                                                                            <td>{rec.tnvf_to if rec.tnvf_to else ''}</td>
                                                                            <td>{rec.tnvf_amount if rec.tnvf_amount else ''}</td>
                                                                            <td>{rec.tnvf_purpose if rec.tnvf_purpose else ''}</td>
                                                                  </tr>

                                                            """
        html_content += f"""
         </tbody> 
                                                                        </table>
                                                        <div class="button-container">
                                                            <p>Total Rate: {self.total_rate}</p>
                                                        </div>"""

        html_content += f"""

                        <div class="button-container">
                            <a href='{approval_url}' style="background-color: green; margin-right: 20px; margin-top: 20px;" class="button">Approve</a>
                            <a href='{disapproval_url}' style="background-color: red; margin-right: 20px; margin-top: 20px;" class="button">Disapprove</a>
                            <a href="{self.generate_odoo_link()}" style="background-color: blue; margin-right: 20px; margin-top: 20px;" class="button">Dashboard</a>
                        </div>"""

        html_content += """
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

    def submit_for_disapproval(self):
        for rec in self:
            res = self.env["approver.setup"].search([
                ("dept_name", "=", rec.department_id.dept_name.name),
                ("approval_type", '=', rec.form_request_type)
            ])
            if rec.approver_id and rec.approval_stage < res.no_of_approvers:
                if rec.approval_stage == 1:
                    recipient_list = []
                    if self.department_id and self.department_id.set_second_approvers:
                        for approver in self.department_id.set_second_approvers:
                            if approver.approver_email:
                                recipient_list.append(approver.approver_email)
                    self.send_to_final_approver_email_disapproved(recipient_list)
                if rec.approval_stage == 2:
                    recipient_list = []
                    if self.department_id and self.department_id.set_third_approvers:
                        for approver in self.department_id.set_third_approvers:
                            if approver.approver_email:
                                recipient_list.append(approver.approver_email)
                    self.send_to_final_approver_email_disapproved(recipient_list)
                if rec.approval_stage == 3:
                    recipient_list = []
                    if self.department_id and self.department_id.set_fourth_approvers:
                        for approver in self.department_id.set_fourth_approvers:
                            if approver.approver_email:
                                recipient_list.append(approver.approver_email)
                    self.send_to_final_approver_email_disapproved(recipient_list)
                if rec.approval_stage == 4:
                    recipient_list = []
                    if self.department_id and self.department_id.set_fifth_approvers:
                        for approver in self.department_id.set_fifth_approvers:
                            if approver.approver_email:
                                recipient_list.append(approver.approver_email)
                    self.send_to_final_approver_email_disapproved(recipient_list)
                rec.approval_stage += 1

    def send_to_final_approver_email_disapproved(self, recipient_list):
        conn = self.main_connection()
        sender = conn['sender']
        host = conn['host']
        port = conn['port']
        username = conn['username']
        password = conn['password']

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        token = self.generate_token()

        approval_url = "{}/dex_form_request_approval/request/tnvf_approve/{}".format(base_url, token)
        disapproval_url = "{}/dex_form_request_approval/request/tnvf_disapprove/{}".format(base_url, token)

        token = self.generate_token()
        self.write({'approval_link': token})

        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))

        msg['To'] = ', '.join(recipient_list)
        msg[
            'Subject'] = f"{re.sub(r'[-_]', ' ', self.form_request_type).title() if self.approval_status else ''} Request has been {re.sub(r'[-_]', ' ', self.approval_status).title() if self.approval_status else ''} [{self.name}]"
        html_content = """
                    <!DOCTYPE html>
                        <html lang="en">
                        <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Invoice Template</title>
                        <style>
                            body {
                                font-family: Arial, sans-serif;
                                margin: 0;
                                padding: 20px;
                            }
                            .container {
                                max-width: 800px;
                                margin: 0 auto;
                                border: 1px solid #ccc;
                                padding: 20px;
                                position: relative;
                            }
                            .header {
                                text-align: center;
                                margin-bottom: 20px;
                            }
                            .invoice-number {
                                position: absolute;
                                top: 20px;
                                right: 20px;
                            }
                            table {
                                width: 100%;
                                border-collapse: collapse;
                                margin-top: 20px;
                            }
                            th, td {
                                border: 1px solid #ddd;
                                padding: 8px;
                                text-align: left;
                            }
                            th {
                                background-color: #f2f2f2;
                            }
                            .button-container {
                                text-align: center;
                                margin-top: 20px;
                            }
                            .button {
                                padding: 10px 20px;
                                margin: 0 10px;
                                border: none;
                                border-radius: 5px;
                                cursor: pointer;
                                font-size: 16px;
                                color: white;
                                transition: background-color 0.3s;
                            }
                            .button:hover {
                                background-color: grey;
                            }
                        </style>
                        </head>
                        <body> """

        html_content += f""" 
                            <div class="container">
                                <div class="header">
                                    <h2>{re.sub(r'[-_]', ' ', self.form_request_type).title() if self.approval_status else ''} Request</h2>
                                    <p>Date: {self.create_date.strftime("%m-%d-%y")}</p>
                                    <p>Request by: {self.requesters_id.name}</p>
                                </div>
                                <div class="invoice-number" style='text-align: center'>
                                    <p>Serial Number: </br> {self.name}</p>
                                </div>
                                <div class="item-details">
                                    <h3>Item Details</h3>
                                    <p>Status: {'To Approve' if self.approval_status == 'draft' else re.sub(r'[-_]', ' ', self.approval_status).title()}</p>
                                    <p>Item Requested: {re.sub(r'[-_]', ' ', self.form_request_type).title() if self.approval_status else ''}</p>
                                    <p>Approved by: {self.env.user.name if self.env.user else ''}</p>
                                    <p>Transport Vehicle: {self.transport_vehicle_type.tnv_type if self.transport_vehicle_type else ''}</p>
                                    <p>Cargo Type: {self.cargo_type if self.cargo_type else ''}</p>
                                </div>"""

        html_content += """
                                                <table>
                                                    <thead>
                                                        <tr>
                                                            <th>Personnel</th>
                                                            <th>Package</th>
                                                            <th>From</th>
                                                            <th>To</th>
                                                            <th>Rate</th>
                                                            <th>Purpose</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                    """
        for rec in self.tnvf_ids:
            html_content += f"""

                                                                  <tr>
                                                                            <td>{rec.tnvf_personnel if rec.tnvf_personnel else ''}</td>
                                                                            <td>{rec.tnvf_package if rec.tnvf_package else ''}</td>
                                                                            <td>{rec.tnvf_from if rec.tnvf_from else ''}</td>
                                                                            <td>{rec.tnvf_to if rec.tnvf_to else ''}</td>
                                                                            <td>{rec.tnvf_amount if rec.tnvf_amount else ''}</td>
                                                                            <td>{rec.tnvf_purpose if rec.tnvf_purpose else ''}</td>
                                                                  </tr>

                                                            """
        html_content += f"""
                                                    </tbody> 
                                                     </table>
                                                        <div class="button-container">
                                                            <p>Total Rate: {self.total_rate}</p>
                                                        </div>"""

        html_content += f"""

                                <div class="button-container">
                                    <a href='{approval_url}' style="background-color: green; margin-right: 20px; margin-top: 20px;" class="button">Approve</a>
                                    <a href='{disapproval_url}' style="background-color: red; margin-right: 20px; margin-top: 20px;" class="button">Disapprove</a>
                                    <a href="{self.generate_odoo_link()}" style="background-color: blue; margin-right: 20px; margin-top: 20px;" class="button">Dashboard</a>
                                </div>"""

        html_content += """
                        </body>
                        </html>
                """

        msg.attach(MIMEText(html_content, 'html'))

        try:
            smtpObj = smtplib.SMTP(host, port)
            smtpObj.login(username, password)
            smtpObj.sendmail(sender, recipient_list, msg.as_string())

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

    def create_bill(self):
        xml_id = 'dex_form_request_approval.dex_form_request_create_bill_view_form'
        model_name = 'create.bill.wizard'
        tnvf_lines = [{
            'label': (
                'This request ({}) was made by: ({}), using transport vehicle ({}), with cargo type ({}), with package or personnel ({})').format(
                self.name,
                self.requesters_id.name,
                self.transport_vehicle_type.tnv_type,
                self.cargo_type,
                line.tnvf_personnel if line.tnvf_personnel else line.tnvf_package),
            'tnvf_personnel': line.tnvf_personnel,
            'tnvf_package': line.tnvf_package,
            'tnvf_from': line.tnvf_from,
            'tnvf_to': line.tnvf_to,
            'tnvf_amount': line.tnvf_amount,
            'tnvf_purpose': line.tnvf_purpose,
        } for line in self.tnvf_ids]

        datas = {
            'name': self.name,
            'requesters_id': self.requesters_id,
            'transport_vehicle_type': self.transport_vehicle_type,
            'transport_vehicle_type_rate': self.transport_vehicle_type_rate,
            'total_rate': self.total_rate,
            'cargo_type': self.cargo_type,
            'currency_id': self.currency_id,
            'journal_id': self.journal_id,
            'state': self.state,
            'tnvf_lines': tnvf_lines,
            'xml_id': xml_id,
            'model_name': model_name,
        }

        action = self.create_bill_function(datas)

        action['context'].update({'link_field_name': 'transport_network_vehicle_ids'})
        return action

    def test(self):
        pass

    @api.onchange('cargo_type')
    def onchange_cargo_type(self):
        for rec in self:
            for r in rec.tnvf_ids:
                r.tnvf_from = False
                r.tnvf_to = False
                r.tnvf_amount = False
                r.tnvf_purpose = False

                if rec.cargo_type == 'package':
                    r.tnvf_personnel = False
                elif rec.cargo_type == 'personnel':
                    r.tnvf_package = False
                else:
                    pass


class TransportNetworkVehicleFormLine(models.Model):
    _name = 'transport.network.vehicle.form.line'

    tnvf_lines = fields.Many2one('transport.network.vehicle.form', string='Line Ids')

    tnvf_personnel = fields.Char(string='Personnel')
    tnvf_package = fields.Char(string='Package')
    tnvf_from = fields.Char(string='From')
    tnvf_to = fields.Char(string='To')
    tnvf_amount = fields.Float(string='Rate')
    tnvf_purpose = fields.Char(string='Purpose')
