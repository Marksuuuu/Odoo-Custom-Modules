# -*- coding: utf-8 -*-
import datetime
import hashlib
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

# from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'department.approvers']

    approver_id = fields.Many2one('hr.employee', string="Approver", domain=lambda self: self.get_approver_domain())
    approval_stage = fields.Integer(default=1)
    department_id = fields.Many2one('account.analytic.account', string="Department", store=True)
    to_approve = fields.Boolean()
    to_approve_po = fields.Boolean()
    show_submit_request = fields.Boolean()
    approval_stock_state = fields.Selection(
        selection=[('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'),
                   ('disapprove', 'Disapproved'), ('cancel', 'Cancelled')],
        default='draft')

    state_blanket_order = fields.Selection([('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'),
                                            ('disapprove', 'Disapproved'), ('cancel', 'Cancelled')], default='draft')
    approval_status = fields.Selection(
        selection=[('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'),
                   ('disapprove', 'Disapproved'), ('cancel', 'Cancelled')], string='Status')

    disapproval_reason = fields.Char(string="Reason for Disapproval")
    # show_request = fields.Char()
    approval_type_id = fields.Many2one('purchase.approval.types')
    approval_id = fields.Many2one('purchase.approval')
    is_approver = fields.Boolean(compute="compute_approver")

    # New fields
    initial_approver_name = fields.Char()
    second_approver_name = fields.Char()
    third_approver_name = fields.Char()
    fourth_approver_name = fields.Char()
    final_approver_name = fields.Char()

    approval_link = fields.Char('Approval link')
    check_status = fields.Char(compute='compute_check_status', store=True)
    approver_count = fields.Integer(compute='_compute_approver_count', store=True)
    date_today = fields.Char()

    initial_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    second_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    third_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    fourth_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    final_approver_job_title = fields.Char(compute='get_approver_title', store=True)

    initial_approver_email = fields.Char()
    second_approver_email = fields.Char()
    third_approver_email = fields.Char()
    fourth_approver_email = fields.Char()
    final_approver_email = fields.Char()

    initial_approval_date = fields.Char()
    second_approval_date = fields.Char()
    third_approval_date = fields.Char()
    fourth_approval_date = fields.Char()
    final_approval_date = fields.Char()

    purchase_rep_email = fields.Char(related="user_id.login", store=True)

    ## New Fields ##

    @api.depends('approval_status', 'approval_stock_state')
    def get_approvers_email(self):
        """
        Retrieves the email addresses of the relevant approvers based on approval status and approval_stock_state.

        Side Effects:
            Updates the email fields of the instance with the appropriate approver emails.
        """
        for rec in self:
            if rec.approval_status == 'approved' or rec.approval_stock_state == 'approved':
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

                rec.purchase_rep_email = self.purchase_rep_email

            elif rec.approval_status == 'disapprove' or rec.approval_stock_state == 'disapprove':
                res = self.env["department.approvers"].search(
                    [("dept_name", "=", rec.department_id.id), ("approval_type.name", '=', 'Inventory Approval')])

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

                rec.purchase_rep_email = self.purchase_rep_email

    @api.depends('initial_approver_name', 'second_approver_name', 'third_approver_name', 'fourth_approver_name',
                 'final_approver_name')
    def get_approver_title(self):
        """
           Fetches the job title of the specified approvers.

           This method iterates over each record and searches for the specified approvers by their names.
           If an approver is found, the corresponding job title and work email are assigned to the record's fields.

        """
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

    # this retrieves the current date, formats it as day-month-year, and assigns the formatted date
    def getCurrentDate(self):
        date_now = datetime.datetime.now()
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

    @api.depends('department_id')
    def _compute_approver_count(self):
        """
            Computes the total number of approvers for the department.

            This method is triggered whenever the 'department_id' field is modified.
            It searches for department approvers associated with the department and purchase requests.
            The count of individual approvers is accumulated to determine the total number of approvers for the department.

        """
        for record in self:
            department_approvers = self.env['department.approvers'].search(
                [('dept_name', '=', record.department_id.id), ("approval_type.name", '=', 'Inventory Approval')])
            count = 0
            for approver in department_approvers:
                count += approver.no_of_approvers
            record.approver_count = count

    # this check the status based on approval status and approval_stock_state.
    @api.depends('approval_status', 'approval_stock_state')
    def compute_check_status(self):
        """
        When installing approval_module_extension in this method compute_check_status comment out the for loop first.
        So it prevents automatically sending of email to already approved or disapproved PR/PO.
        After successfully installing the module. You can now uncomment the for loop and Upgrade the module.
        """
        print('Testing')
        for rec in self:
            if rec.approval_status == 'approved' or rec.approval_stock_state == 'approved':
                rec.get_approvers_email()
                rec.submit_to_final_approver()
            elif rec.approval_status == 'disapprove' or rec.approval_stock_state == 'disapprove':
                rec.get_approvers_email()
                rec.submit_for_disapproval()

    def update_check_status(self):
        self.check_status = False
        self.check_status = True

    def approval_dashboard_link(self):
        # Approval Dashboard Link Section
        approval_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        approval_action = self.env['ir.actions.act_window'].search(
            [('name', '=', 'Purchase Request Approval Dashboard')], limit=1)
        action_id = approval_action.id

        odoo_params = {
            "action": action_id,
        }

        query_string = '&'.join([f'{key}={value}' for key, value in odoo_params.items()])
        list_view_url = f"{approval_base_url}/web?debug=0#{query_string}"
        return list_view_url

    def generate_odoo_link(self):
        # Generate Odoo Link Section
        action = self.env['ir.actions.act_window'].search([('res_model', '=', 'stock.picking')], limit=1)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        result = re.sub(r'\((.*?)\)', '', str(action)).replace(',', '')
        res = f"{result},{action.id}"
        result = re.sub(r'\s*,\s*', ',', res)

        menu = self.env['ir.ui.menu'].search([('action', '=', result)], limit=1)
        params = {
            "id": self.id,
            "action": action.id,
            "model": "stock.picking",
            "view_type": "form",
            "cids": 1,
            "menu_id": menu.id
        }
        query_params = "&".join(f"{key}={value}" for key, value in params.items())
        pr_form_link = f"{base_url}/web#{query_params}"
        return pr_form_link

    def generate_token(self):
        now = datetime.datetime.now()
        token = "{}-{}-{}-{}".format(self.id, self.name, self.env.user.id, now)
        return hashlib.sha256(token.encode()).hexdigest()

    # Initial Approver Sending of Email
    def submit_for_approval(self):
        # Approval Dashboard Link Section
        approval_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        approval_action = self.env['ir.actions.act_window'].search(
            [('name', '=', 'Purchase Request Approval Dashboard')], limit=1)
        action_id = approval_action.id

        odoo_params = {
            "action": action_id,
        }

        query_string = '&'.join([f'{key}={value}' for key, value in odoo_params.items()])
        approval_list_view_url = f"{approval_base_url}/web?debug=0#{query_string}"

        # Generate Odoo Link Section
        odoo_action = self.env['ir.actions.act_window'].search([('res_model', '=', 'stock.picking')], limit=1)
        odoo_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        odoo_result = re.sub(r'\((.*?)\)', '', str(odoo_action)).replace(',', '')
        odoo_res = f"{odoo_result},{odoo_action.id}"
        odoo_result = re.sub(r'\s*,\s*', ',', odoo_res)

        odoo_menu = self.env['ir.ui.menu'].search([('action', '=', odoo_result)], limit=1)
        odoo_params = {
            "id": self.id,
            "action": odoo_action.id,
            "model": "stock.picking",
            "view_type": "form",
            "cids": 1,
            "menu_id": odoo_menu.id
        }
        odoo_query_params = "&".join(f"{key}={value}" for key, value in odoo_params.items())
        pr_form_link = f"{odoo_base_url}/web#{odoo_query_params}"

        self.generate_odoo_link()
        self.approval_dashboard_link()

        fetch_getEmailReceiver = self.approver_id.work_email  # self.approver_id.work_email DEFAULT RECEIVER CHANGE IT TO IF YOU WANT ----> IF YOU WANT TO SET AS DEFAULT OR ONLY ONE ##
        self.sendingEmail(fetch_getEmailReceiver, pr_form_link, approval_list_view_url)

        self.write({
            'approval_status': 'to_approve',
            'approval_stock_state': 'to_approve',
            'to_approve': True,
            'show_submit_request': False
        })

    def sendingEmail(self, fetch_getEmailReceiver, pr_form_link, approval_list_view_url):
        sender = 'noreply@teamglac.com'
        host = "192.168.1.114"
        port = 25
        username = "noreply@teamglac.com"
        password = "noreply"

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        token = self.generate_token()

        approval_url = "{}/inventory_approval/request/approve/{}".format(base_url, token)
        disapproval_url = "{}/inventory_approval/request/disapprove/{}".format(base_url, token)

        self.write({'approval_link': token})
        print(self.approval_link)
        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))
        msg['To'] = fetch_getEmailReceiver
        msg['Subject'] = 'Inventory Request For Approval [' + self.name + ']'

        html_content = """
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            table {
              border-collapse: collapse;
              width: 100%;
              font-size: 16px;
            }

            * {
              font-size: 16px;
            }

            th, td {
              text-align: left;
              padding: 10px;
            }

            tr:nth-child(even){background-color: #f2f2f2}

            th {
              background-color: #5f5e97;
              color: white;
            }
            .button {
              background-color: #04AA6D; /* Green */
              border: none;
              color: white;
              padding: 15px 32px;
              text-align: center;
              text-decoration: none;
              display: inline-block;
              font-size: 16px;
              margin: 4px 2px;
              cursor: pointer;
            }
            .button2 {background-color: #008CBA;} /* Blue */
            .button3 {background-color: #f44336;} /* Red */ 
            .button4 {background-color: #e7e7e7; color: black;} /* Gray */ 
            .button5 {background-color: #555555;} /* Black */
            </style>
            </head>
            <body>
        """

        html_content += f"""
            <dt><b>{self.name}</b></dt>
            <br></br>
            <dd>Requested by: &nbsp;&nbsp;{self.user_id.name if self.name != False else ""}</dd>
            <dd>Date Requested: &nbsp;&nbsp;{datetime.datetime.now() if self.name != False else ""}</dd>
            <dd>Source Document: &nbsp;&nbsp;{self.origin if self.origin != False else ""}</dd>
            <br></br>
            <span><b>ITEMS REQUESTED</b></span>
            <br/>
            <br></br>
        """

        html_content += """
            <table style='margin-bottom: 50px;'>
                <tr>
                    <th>Product</th>
                    <th>Description</th>
                    <th>Quantity</th>
                    <th>EOH</th>
                    <th>Remarks</th>
                </tr>
        """

        for line in self.move_ids_without_package:
            html_content += f"""
                <tr>
                    <td>{line.product_id.name}</td>
                    <td>{line.product_id.name + '[' + line.product_id.name + ']'}</td>
                    <td>{line.quantity_done}</td>
                     <td>{line.product_id.qty_available}</td>
                    <td>{self.note}</td>
                </tr>
            """

        html_content += f"""
            </table>

            <a href="{approval_url}" style='background-color: green;
                border: none;
                color: white;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                padding: 10px 24px;
                border-radius: 50px;
                cursor: pointer;'>APPROVE</a>

            <a href="{disapproval_url}" style='background-color: red;
                border: none;
                color: white;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                padding: 10px 24px;
                border-radius: 50px;
                cursor: pointer;'>DISAPPROVE</a>
            </body>
            </html>
        """

        msg.attach(MIMEText(html_content, 'html'))

        try:
            smtpObj = smtplib.SMTP(host, port)
            smtpObj.login(username, password)
            smtpObj.sendmail(sender, fetch_getEmailReceiver, msg.as_string())

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

    # Next Approver Sending of Email
    def submit_to_next_approver(self):
        # Approval Dashboard Link Section

        approval_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        approval_action = self.env['ir.actions.act_window'].search(
            [('name', '=', 'Purchase Request Approval Dashboard')], limit=1)
        action_id = approval_action.id
        odoo_params = {
            "action": action_id,
        }

        query_string = '&'.join([f'{key}={value}' for key, value in odoo_params.items()])
        approval_list_view_url = f"{approval_base_url}/web?debug=0#{query_string}"

        # Generate Odoo Link Section
        odoo_action = self.env['ir.actions.act_window'].search([('res_model', '=', 'stock.picking')], limit=1)
        odoo_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        odoo_result = re.sub(r'\((.*?)\)', '', str(odoo_action)).replace(',', '')
        odoo_res = f"{odoo_result},{odoo_action.id}"
        odoo_result = re.sub(r'\s*,\s*', ',', odoo_res)

        odoo_menu = self.env['ir.ui.menu'].search([('action', '=', odoo_result)], limit=1)
        odoo_params = {
            "id": self.id,
            "action": odoo_action.id,
            "model": "stock.picking",
            "view_type": "form",
            "cids": 1,
            "menu_id": odoo_menu.id
        }
        odoo_query_params = "&".join(f"{key}={value}" for key, value in odoo_params.items())
        pr_form_link = f"{odoo_base_url}/web#{odoo_query_params}"

        self.generate_odoo_link()
        self.approval_dashboard_link()

        fetch_getEmailReceiver = self.approver_id.work_email  # self.approver_id.work_email DEFAULT RECEIVER CHANGE IT TO IF YOU WANT ----> IF YOU WANT TO SET AS DEFAULT OR ONLY ONE ##
        self.sending_email_to_next_approver(fetch_getEmailReceiver, pr_form_link, approval_list_view_url)

        self.write({
            'approval_status': 'to_approve',
            'approval_stock_state': 'to_approve',
            'to_approve': True,
            'show_submit_request': False
        })

    def sending_email_to_next_approver(self, fetch_getEmailReceiver, pr_form_link, approval_list_view_url):
        sender = 'noreply@teamglac.com'
        host = "192.168.1.114"
        port = 25
        username = "noreply@teamglac.com"
        password = "noreply"

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        token = self.generate_token()

        approval_url = "{}/inventory_approval/request/approve/{}".format(base_url, token)
        disapproval_url = "{}/inventory_approval/request/disapprove/{}".format(base_url, token)

        self.write({'approval_link': token})
        print(token)
        print("main next", self.approval_link)

        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))
        msg['To'] = fetch_getEmailReceiver
        msg['Subject'] = 'Inventory Request For Approval [' + self.name + ']'

        html_content = """
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            table {
              border-collapse: collapse;
              width: 100%;
              font-size: 16px;
            }

            * {
              font-size: 16px;
            }

            th, td {
              text-align: left;
              padding: 10px;
            }

            tr:nth-child(even){background-color: #f2f2f2}

            th {
              background-color: #5f5e97;
              color: white;
            }
            .button {
              background-color: #04AA6D; /* Green */
              border: none;
              color: white;
              padding: 15px 32px;
              text-align: center;
              text-decoration: none;
              display: inline-block;
              font-size: 16px;
              margin: 4px 2px;
              cursor: pointer;
            }
            .button2 {background-color: #008CBA;} /* Blue */
            .button3 {background-color: #f44336;} /* Red */ 
            .button4 {background-color: #e7e7e7; color: black;} /* Gray */ 
            .button5 {background-color: #555555;} /* Black */
            </style>
            </head>
            <body>
        """

        html_content += f"""
            <dt><b>{self.name}</b></dt>
            <br></br>
            <dd>Requested by: &nbsp;&nbsp;{self.user_id.name if self.name != False else ""}</dd>
            <dd>Date Requested: &nbsp;&nbsp;{datetime.datetime.now() if self.name != False else ""}</dd>
            <dd>Source Document: &nbsp;&nbsp;{self.origin if self.origin != False else ""}</dd>
            <br></br>
            <span><b>ITEMS REQUESTED</b></span>
            <br/>
            <br></br>
        """

        html_content += """
            <table style='margin-bottom: 50px;'>
                <tr>
                    <th>Product</th>
                    <th>Description</th>
                    <th>Quantity</th>
                    <th>EOH</th>
                    <th>Remarks</th>
                </tr>
        """

        for line in self.move_ids_without_package:
            html_content += f"""
                <tr>
                    <td>{line.product_id.name}</td>
                    <td>{line.product_id.name + '[' + line.product_id.name + ']'}</td>
                    <td>{line.quantity_done}</td>
                     <td>{line.product_id.qty_available}</td>
                    <td>{self.note}</td>
                </tr>
            """

        html_content += f"""
            </table>

            <a href="{approval_url}" style='background-color: green;
                border: none;
                color: white;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                padding: 10px 24px;
                border-radius: 50px;
                cursor: pointer;'>APPROVE</a>

            <a href="{disapproval_url}" style='background-color: red;
                border: none;
                color: white;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                padding: 10px 24px;
                border-radius: 50px;
                cursor: pointer;'>DISAPPROVE</a>
            </body>
            </html>
        """

        msg.attach(MIMEText(html_content, 'html'))

        try:
            smtpObj = smtplib.SMTP(host, port)
            smtpObj.login(username, password)
            smtpObj.sendmail(sender, fetch_getEmailReceiver, msg.as_string())

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

    # PR is DISAPPROVED
    def submit_for_disapproval(self):
        # Generate Odoo Link Section
        odoo_action = self.env['ir.actions.act_window'].search([('res_model', '=', 'stock.picking')], limit=1)
        odoo_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        odoo_result = re.sub(r'\((.*?)\)', '', str(odoo_action)).replace(',', '')
        odoo_res = f"{odoo_result},{odoo_action.id}"
        odoo_result = re.sub(r'\s*,\s*', ',', odoo_res)

        odoo_menu = self.env['ir.ui.menu'].search([('action', '=', odoo_result)], limit=1)
        odoo_params = {
            "id": self.id,
            "action": odoo_action.id,
            "model": "stock.picking",
            "view_type": "form",
            "cids": 1,
            "menu_id": odoo_menu.id
        }
        odoo_query_params = "&".join(f"{key}={value}" for key, value in odoo_params.items())
        pr_form_link = f"{odoo_base_url}/web#{odoo_query_params}"

        self.generate_odoo_link()

        # fetch_getEmailReceiver = self.approver_id.work_email  # self.approver_id.work_email DEFAULT RECEIVER CHANGE IT TO IF YOU WANT ----> IF YOU WANT TO SET AS DEFAULT OR ONLY ONE ##
        # self.send_disapproval_email(fetch_getEmailReceiver, pr_form_link)
        email1 = self.initial_approver_email if self.initial_approver_email else ""
        email2 = self.second_approver_email if self.second_approver_email else ""
        email3 = self.third_approver_email if self.third_approver_email else ""
        email4 = self.fourth_approver_email if self.fourth_approver_email else ""
        email5 = self.final_approver_email if self.final_approver_email else ""
        email6 = self.purchase_rep_email if self.purchase_rep_email else ""

        self.send_disapproval_email([email1, email2, email3, email4, email5, email6], pr_form_link)

    def send_disapproval_email(self, recipient_list, pr_form_link):
        sender = 'noreply@teamglac.com'
        host = "192.168.1.114"
        port = 25
        username = "noreply@teamglac.com"
        password = "noreply"

        token = self.generate_token()
        self.write({'approval_link': token})

        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))

        msg['To'] = ', '.join(recipient_list)
        msg['Subject'] = 'Inventory Request Disapproved [' + self.name + ']'

        html_content = """
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            table {
              border-collapse: collapse;
              width: 100%;
              font-size: 16px;
            }

            * {
              font-size: 16px;
            }

            th, td {
              text-align: left;
              padding: 10px;
            }

            tr:nth-child(even){background-color: #f2f2f2}

            th {
              background-color: #5f5e97;
              color: white;
            }
            .button {
              background-color: #04AA6D; /* Green */
              border: none;
              color: white;
              padding: 15px 32px;
              text-align: center;
              text-decoration: none;
              display: inline-block;
              font-size: 16px;
              margin: 4px 2px;
              cursor: pointer;
            }
            .button2 {background-color: #008CBA;} /* Blue */
            .button3 {background-color: #f44336;} /* Red */ 
            .button4 {background-color: #e7e7e7; color: black;} /* Gray */ 
            .button5 {background-color: #555555;} /* Black */
            </style>
            </head>
            <body>
        """

        html_content += f"""
            <dt><b>{self.name}</b></dt>
            <br></br>
            <dd>Requested by: &nbsp;&nbsp;{self.user_id.name if self.name != False else ""}</dd>
            <dd>Date Requested: &nbsp;&nbsp;{datetime.datetime.now() if self.name != False else ""}</dd>
            <dd>Source Document: &nbsp;&nbsp;{self.origin if self.origin != False else ""}</dd>
            <br></br>
            <span><b>ITEMS REQUESTED</b></span>
            <br/>
            <br></br>
        """

        html_content += """
            <table style='margin-bottom: 50px;'>
                <tr>
                    <th>Product</th>
                    <th>Description</th>
                    <th>Quantity</th>
                    <th>EOH</th>
                    <th>Remarks</th>
                </tr>
        """

        for line in self.move_ids_without_package:
            html_content += f"""
                <tr>
                    <td>{line.product_id.name}</td>
                    <td>{line.product_id.name + '[' + line.product_id.name + ']'}</td>
                    <td>{line.quantity_done}</td>
                    <td>{line.product_id.qty_available}</td>
                    <td>{self.note}</td>
                </tr>
            """

        html_content += """
            </table>

            <a href="{approval_url}" style='background-color: green;
                border: none;
                color: white;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                padding: 10px 24px;
                border-radius: 50px;
                cursor: pointer;'>APPROVE</a>

            <a href="{disapproval_url}" style='background-color: red;
                border: none;
                color: white;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                padding: 10px 24px;
                border-radius: 50px;
                cursor: pointer;'>DISAPPROVE</a>
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

    # PR is approved by final approver
    def submit_to_final_approver(self):
        # fetch_getEmailReceiver = self.approver_id.work_email  # self.approver_id.work_email DEFAULT RECEIVER CHANGE IT TO IF YOU WANT ----> IF YOU WANT TO SET AS DEFAULT OR ONLY ONE ##
        # self.send_to_final_approver_email(fetch_getEmailReceiver)

        email1 = self.initial_approver_email if self.initial_approver_email else ""
        email2 = self.second_approver_email if self.second_approver_email else ""
        email3 = self.third_approver_email if self.third_approver_email else ""
        email4 = self.fourth_approver_email if self.fourth_approver_email else ""
        email5 = self.final_approver_email if self.final_approver_email else ""
        email6 = self.purchase_rep_email if self.purchase_rep_email else ""

        self.send_to_final_approver_email([email1, email2, email3, email4, email5, email6])

    def send_to_final_approver_email(self, recipient_list):
        sender = 'noreply@teamglac.com'
        host = "192.168.1.114"
        port = 25
        username = "noreply@teamglac.com"
        password = "noreply"

        token = self.generate_token()
        self.write({'approval_link': token})

        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))

        msg['To'] = ', '.join(recipient_list)
        msg['Subject'] = 'Inventory Request Approved [' + self.name + ']'

        html_content = """
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            table {
              border-collapse: collapse;
              width: 100%;
              font-size: 16px;
            }

            * {
              font-size: 16px;
            }

            th, td {
              text-align: left;
              padding: 10px;
            }

            tr:nth-child(even){background-color: #f2f2f2}

            th {
              background-color: #5f5e97;
              color: white;
            }
            .button {
              background-color: #04AA6D; /* Green */
              border: none;
              color: white;
              padding: 15px 32px;
              text-align: center;
              text-decoration: none;
              display: inline-block;
              font-size: 16px;
              margin: 4px 2px;
              cursor: pointer;
            }
            .button2 {background-color: #008CBA;} /* Blue */
            .button3 {background-color: #f44336;} /* Red */ 
            .button4 {background-color: #e7e7e7; color: black;} /* Gray */ 
            .button5 {background-color: #555555;} /* Black */
            </style>
            </head>
            <body>
        """

        html_content += f"""
            <dt><b>{self.name}</b></dt>
            <br></br>
            <dd>Requested by: &nbsp;&nbsp;{self.user_id.name if self.name != False else ""}</dd>
            <dd>Date Requested: &nbsp;&nbsp;{datetime.datetime.now() if self.name != False else ""}</dd>
            <dd>Source Document: &nbsp;&nbsp;{self.origin if self.origin != False else ""}</dd>
            <br></br>
            <span><b>ITEMS REQUESTED</b></span>
            <br/>
            <br></br>
        """

        html_content += """
            <table style='margin-bottom: 50px;'>
                <tr>
                    <th>Product</th>
                    <th>Description</th>
                    <th>Quantity</th>
                    <th>EOH</th>
                    <th>Remarks</th>
                </tr>
        """

        for line in self.move_ids_without_package:
            html_content += f"""
                <tr>
                    <td>{line.product_id.name}</td>
                    <td>{line.product_id.name + '[' + line.product_id.name + ']'}</td>
                    <td>{line.quantity_done}</td>
                     <td>{line.product_id.qty_available}</td>
                    <td>{self.note}</td>
                </tr>
            """

        html_content += """
            </table>

            <a href="{approval_url}" style='background-color: green;
                border: none;
                color: white;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                padding: 10px 24px;
                border-radius: 50px;
                cursor: pointer;'>APPROVE</a>

            <a href="{disapproval_url}" style='background-color: red;
                border: none;
                color: white;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                padding: 10px 24px;
                border-radius: 50px;
                cursor: pointer;'>DISAPPROVE</a>
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

    def action_in_progress(self):
        # self.ensure_one()
        # if not all(obj.move_ids_without_package for obj in self):
        #     raise UserError(_("You cannot confirm agreement {} because there is no product line.").format(self.name))
        # if self.type_id.quantity_copy == 'none' and self.vendor_id:
        #     for requisition_line in self.move_ids_without_package:
        #         if requisition_line.price_unit <= 0.0:
        #             raise UserError(_('You cannot confirm the blanket order without price.'))
        #         if requisition_line.product_qty <= 0.0:
        #             raise UserError(_('You cannot confirm the blanket order without quantity.'))
        #         requisition_line.create_supplier_info()
        #     self.write({'approval_stock_state': 'to_approve'})
        # else:
        #     self.write({'approval_stock_state': 'to_approve'})
        # # Set the sequence number regarding the requisition type
        # if self.name == 'New':
        #     if self.is_quantity_copy != 'none':
        #         self.name = self.env['ir.sequence'].next_by_code('stock.picking.purchase.tender')
        #     else:
        #         self.name = self.env['ir.sequence'].next_by_code('stock.picking.blanket.order')

        self.write({
            'show_submit_request': True
        })

    # def _compute_approver(self):
    #     for rec in self:
    #         if self.env.user == rec.approver_id.user_id:
    #             self.update({
    #                 'is_approver': True,
    #
    #             })
    #         else:
    #             self.update({
    #                 'is_approver': False,
    #             })

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

    @api.onchange('department_id', 'approval_stage')
    def get_approver_domain(self):
        for rec in self:
            domain = []
            res = self.env["department.approvers"].search(
                [("dept_name", "=", rec.department_id.id), ("approval_type.name", '=', 'Inventory Approval')])

            if rec.department_id and rec.approval_stage == 1:
                try:
                    approver_dept = [x.first_approver.id for x in res.set_first_approvers]
                    rec.approver_id = approver_dept[0]
                    domain.append(('id', '=', approver_dept))

                except IndexError:
                    raise UserError(_("No Approvers set for {}!").format(rec.department_id.name))

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

    @api.depends('approval_stage')
    def pr_approve_request(self):
        for rec in self:
            res = self.env["department.approvers"].search(
                [("dept_name", "=", rec.department_id.id), ("approval_type.name", '=', 'Inventory Approval')])

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

                    self.submit_to_next_approver()
                    self.getCurrentDate()

                if rec.approval_stage == 2:
                    if self.second_approver_name is None:
                        raise UserError('No approver set')
                    else:
                        self.second_approver_name = rec.approver_id.name
                    approver_dept = [x.third_approver.id for x in res.set_third_approvers]

                    self.write({
                        'approver_id': approver_dept[0]
                    })

                    self.submit_to_next_approver()
                    self.getCurrentDate()

                if rec.approval_stage == 3:
                    if self.third_approver_name is None:
                        raise UserError('No approver set')
                    else:
                        self.third_approver_name = rec.approver_id.name

                    approver_dept = [x.fourth_approver.id for x in res.set_fourth_approvers]

                    self.write({
                        'approver_id': approver_dept[0]
                    })

                    self.submit_to_next_approver()
                    self.getCurrentDate()

                if rec.approval_stage == 4:
                    if self.fourth_approver_name is None:
                        raise UserError('No approver set')
                    else:
                        self.fourth_approver_name = rec.approver_id.name

                    approver_dept = [x.fifth_approver.id for x in res.set_fifth_approvers]

                    self.write({
                        'approver_id': approver_dept[0]
                    })

                    self.submit_to_next_approver()
                    self.getCurrentDate()

                rec.approval_stage += 1
            else:
                self.write({
                    'approval_stock_state': 'approved',
                    'approval_status': 'approved',
                    'final_approver_name': rec.approver_id.name,
                })
                self.getCurrentDate()

    def button_cancel(self):
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.approval_stock_state not in ('cancel', 'draft'):
                    raise UserError(
                        _("Unable to cancel this purchase order. You must first cancel the related vendor bills."))

        self.write({'approval_stock_state': 'cancel',
                    'approval_status': 'cancel'})
