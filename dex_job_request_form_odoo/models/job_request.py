import datetime
import hashlib
import re
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import formataddr
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class JobRequest(models.Model):
    _name = 'job.request'
    _inherit = ['job.abstract']
    _rec_name = 'name'
    _order = 'create_date asc'
    _description = 'model for Job Request Data'

    approver_id = fields.Many2one('hr.employee', string="Approver", domain=lambda self: self.get_approver_domain(),
                                  store=True)
    approver_count = fields.Integer(compute='_compute_approver_count', store=True, tracking=True)
    check_status = fields.Char(compute='compute_check_status', store=True, tracking=True)
    supplier_id = fields.Many2one('res.partner', string="Supplier", required=False, tracking=True)
    invoice_or_ref = fields.Char(string='Invoice or Reference', tracking=True)

    workers_requested = fields.Char(string='Workers Requested', tracking=True)

    approved_by = fields.Many2one('res.users', string="Approved By", tracking=True)
    date_approved = fields.Datetime(tracking=True)
    is_approver = fields.Boolean(compute="compute_approver", tracking=True)

    date_from_user = fields.Date(string='Date From', tracking=True)
    total_days_user = fields.Integer(string='Total Days', tracking=True)

    actual_start_date = fields.Date(string='Actual Start Date', tracking=True)
    actual_end_date = fields.Date(string='Actual End Date', tracking=True)
    actual_total_date = fields.Float(string='Actual Total Date', tracking=True)

    connection_wo = fields.Many2one('warehouse.order', tracking=True)

    create_user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user,
                                     tracking=True)
    current_user_groups = fields.Char(string='Current User Groups', compute='_compute_current_user_groups',
                                      tracking=True)

    current_user_groups1 = fields.Char(string='Current User Groups', compute='_compute_current_user_groups1',
                                      tracking=True)

    reason_to_change = fields.Char(string='Reason To Change', tracking=True)
    is_change = fields.Boolean(default=False, tracking=True)
    workers_assigned_when_changed = fields.Many2many('res.users', string='Supervisor Assigned Workers', default=False,
                                                     tracking=True)

    def current_user_that_logged_in(self):
        return self.env.user.name

    def current_time_now(self):
        now = datetime.now()
        return now.strftime("%m/%d/%Y %-I:%M%p").lower()


    @api.depends('current_user_groups1', 'requesters_id')
    def _compute_current_user_groups1(self):
        for record in self:
            # Get the current user
            user = self.env.user

            # Get the model's access control list (ACL)
            acl = self.env['ir.model.access'].search(
                [('model_id', '=', self.env.ref('dex_job_request_form_odoo.model_job_request').id)])

            _logger.info(f'TESTTTT 0000{acl}')

            # Filter ACL to get only those records where current user has access and belongs to one of the target groups
            user_acl_manager = acl.filtered(lambda
                                                r: user.id in r.group_id.users.ids and r.group_id.name == 'Admin')
            user_acl_user = acl.filtered(
                lambda r: user.id in r.group_id.users.ids and r.group_id.name == 'User')

            _logger.info(f'TESTTTT 1{user_acl_manager.name}')

            _logger.info(f'TESTTTT 2{user_acl_user.name}')

            # If the user is in the manager group, set current_user_groups to 'manager'
            if user_acl_manager.name == 'dex_job_request_form_odoo.access_job_request_manager':
                record.current_user_groups1 = 'manager'
                _logger.info(f'TESTTTT 1{record.current_user_groups1}')

            # If the user is in the user group, set current_user_groups1 to 'user'
            elif user_acl_user.name == 'dex_job_request_form_odoo.access_job_request_user':
                record.current_user_groups1 = 'user'
                _logger.info(f'TESTTTT 2{record.current_user_groups1}')
            # If user is not in either group, set current_user_groups1 to an empty string
            else:
                record.current_user_groups1 = ''

    @api.depends('current_user_groups', 'requesters_id')
    def _compute_current_user_groups(self):
        for record in self:
            # Get the current user
            user = self.requesters_id.user_id

            # Get the model's access control list (ACL)
            acl = self.env['ir.model.access'].search(
                [('model_id', '=', self.env.ref('dex_job_request_form_odoo.model_job_request').id)])

            _logger.info(f'TESTTTT 0000{acl}')

            # Filter ACL to get only those records where current user has access and belongs to one of the target groups
            user_acl_manager = acl.filtered(lambda
                                                r: user.id in r.group_id.users.ids and r.group_id.name == 'Admin')
            user_acl_user = acl.filtered(
                lambda r: user.id in r.group_id.users.ids and r.group_id.name == 'User')

            _logger.info(f'TESTTTT 1{user_acl_manager.name}')

            _logger.info(f'TESTTTT 2{user_acl_user.name}')

            # If the user is in the manager group, set current_user_groups to 'manager'
            if user_acl_manager.name == 'dex_job_request_form_odoo.access_job_request_manager':
                record.current_user_groups = 'manager'
                _logger.info(f'TESTTTT 1{record.current_user_groups}')

            # If the user is in the user group, set current_user_groups to 'user'
            elif user_acl_user.name == 'dex_job_request_form_odoo.access_job_request_user':
                record.current_user_groups = 'user'
                _logger.info(f'TESTTTT 2{record.current_user_groups}')
            # If user is not in either group, set current_user_groups to an empty string
            else:
                record.current_user_groups = ''

    @api.depends('actual_start_date', 'actual_end_date')
    def compute_total_date(self):
        for record in self:
            if record.actual_start_date and record.actual_end_date:
                start_date = datetime.strptime(record.actual_start_date, '%Y-%m-%d')
                end_date = datetime.strptime(record.actual_end_date, '%Y-%m-%d')
                total_days = (end_date - start_date).days
                record.actual_total_date = total_days
            else:
                record.actual_total_date = 0.0

    @api.depends('date_from_user', 'date_to_user')
    def on_hold(self):
        self.write({
            'state': 'on_hold'
        })

    def work_done(self):
        self.compute_total_date()
        self.write({
            'state': 'done'
        })

    def ongoing(self):
        self.write({
            'state': 'ongoing'
        })

    def assigned(self):
        self.write({
            'state': 'assigned'
        })

    def cancel(self):
        self.write({
            'state': 'cancelled'
        })

    def rejected(self):
        self.write({
            'state': 'rejected'
        })

    def test(self):
        recipient_list = []
        if self.worker and self.worker.name:
            for res in self.worker:
                if res.name:
                    recipient_list.append(res.name)

        _logger.info(f'TESTTTTTTTTTTTTTT {recipient_list}')

    def get_workers(self):
        recipient_list = []
        for worker in self.workers_assigned_when_changed:
            if worker.name:
                recipient_list.append(worker.name)
        return recipient_list

    def _get_department_domain(self):
        approval_types = self.env['approver.setup'].search([('approval_type', '=', 'job_request')])
        if approval_types:
            return [('id', 'in', approval_types.ids)]

    @api.onchange('requesters_id')
    def _onchange_requesters_id(self):
        if self.requesters_id and self.requesters_id.department_id:
            department_name = self.requesters_id.department_id.name
            approval_type = 'job_request'

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
            [('name', '=', 'Job Request')], limit=1)
        action_id = approval_action.id

        odoo_params = {
            "action": action_id,
        }

        query_string = '&'.join([f'{key}={value}' for key, value in odoo_params.items()])
        approval_list_view_url = f"{approval_base_url}/web?debug=0#{query_string}"

        # Generate Odoo Link Section
        odoo_action = self.env['ir.actions.act_window'].search([('res_model', '=', 'job.request')], limit=1)
        odoo_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        odoo_result = re.sub(r'\((.*?)\)', '', str(odoo_action)).replace(',', '')
        odoo_res = f"{odoo_result},{odoo_action.id}"
        odoo_result = re.sub(r'\s*,\s*', ',', odoo_res)

        odoo_menu = self.env['ir.ui.menu'].search([('action', '=', odoo_result)], limit=1)
        odoo_params = {
            "id": self.id,
            "action": odoo_action.id,
            "model": "job.request",
            "view_type": "form",
            "cids": 1,
            "menu_id": odoo_menu.id
        }
        odoo_query_params = "&".join(f"{key}={value}" for key, value in odoo_params.items())
        form_link = f"{odoo_base_url}/web#{odoo_query_params}"

        get_all_email_receiver = self.approver_id.work_email
        print(get_all_email_receiver)
        print(form_link)

        recipient_list = []
        if self.department_id and self.department_id.set_first_approvers:
            for approver in self.department_id.set_first_approvers:
                if approver.approver_email:
                    recipient_list.append(approver.approver_email)

        # self.notify_to_all(recipient_list)
        # self.sending_email(get_all_email_receiver, form_link, approval_list_view_url)

        self.write({
            'state': 'queue',
        })

    @api.depends('state')
    def compute_check_status(self):
        recipient_list = []
        if self.department_id and self.department_id.set_first_approvers:
            for approver in self.department_id.set_first_approvers:
                if approver.approver_email:
                    recipient_list.append(approver.approver_email)
        if self.requesters_email:
            recipient_list.append(self.requesters_email)

        _logger.info(f'ASDDDDDDDDDDDDD {recipient_list}')
        _logger.info(f'ASDDDDDDDDDDDDD {self.requesters_email}')

        for rec in self:
            if rec.state == 'assigned':
                rec.notify_to_all(recipient_list)
                _logger.info(f'{rec.state} assigned')
            elif rec.state == 'ongoing':
                rec.notify_to_all(recipient_list)
                _logger.info(f'{rec.state} assigned')
            elif rec.state == 'on_hold':
                rec.notify_to_all(recipient_list)
                _logger.info(f'{rec.state} on_hold')
            elif rec.state == 'cancelled':
                rec.notify_to_all(recipient_list)
                _logger.info(f'{rec.state} cancelled')
            elif rec.state == 'rejected':
                rec.notify_to_all(recipient_list)
                _logger.info(f'{rec.state} rejected')
            elif rec.state == 'done':
                rec.notify_to_all(recipient_list)
                _logger.info(f'{rec.state} done')
            elif rec.state == 'queue':
                rec.notify_to_all(recipient_list)
                _logger.info(f'{rec.state} queue')
            else:
                pass

    def generate_token(self):
        now = datetime.now()
        token = "{}-{}-{}-{}".format(self.id, self.name, self.env.user.id, now)
        return hashlib.sha256(token.encode()).hexdigest()

    def generate_odoo_link(self):
        # Generate Odoo Link Section
        action = self.env['ir.actions.act_window'].search([('res_model', '=', 'job.request')], limit=1)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        result = re.sub(r'\((.*?)\)', '', str(action)).replace(',', '')
        res = f"{result},{action.id}"
        result = re.sub(r'\s*,\s*', ',', res)

        menu = self.env['ir.ui.menu'].search([('action', '=', result)], limit=1)
        params = {
            "id": self.id,
            "action": action.id,
            "model": "job.request",
            "view_type": "form",
            "cids": 1,
            "menu_id": menu.id
        }
        query_params = "&".join(f"{key}={value}" for key, value in params.items())
        form_link = f"{base_url}/web#{query_params}"
        return form_link

    def approval_dashboard_link(self):
        # Approval Dashboard Link Section
        approval_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        approval_action = self.env['ir.actions.act_window'].search(
            [('name', '=', 'Job Request')], limit=1)
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
            print(count)
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
                    print(approver_dept)
                    rec.approver_id = approver_dept[0]
                    domain.append(('id', '=', approver_dept))

                except IndexError:
                    raise UserError(_("No Approvers set for {}!").format(rec.department_id.dept_name.name))

            elif rec.department_id and rec.approval_stage == 2:
                approver_dept = [x.second_approver.id for x in res.set_second_approvers]
                print(approver_dept)
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

            print(domain)

            return {'domain': {'approver_id': domain}}

    def generate_pdf(self):
        return self.env.ref('dex_job_request_form_odoo.jrf_odoo_report_id').report_action(self)

    def generate_motivational_quote(self):
        quotes = [
            ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
            ("The only way to do great work is to love what you do.", "Steve Jobs"),
            ("Success is not final, failure is not fatal: It is the courage to continue that counts.",
             "Winston Churchill"),
            ("The only limit to our realization of tomorrow will be our doubts of today.", "Franklin D. Roosevelt"),
            ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
            ("Your limitation—it's only your imagination.", "Unknown"),
            ("Push yourself, because no one else is going to do it for you.", "Unknown"),
            ("Great things never come from comfort zones.", "Unknown"),
            ("Dream it. Wish it. Do it.", "Unknown"),
            ("Success doesn’t just find you. You have to go out and get it.", "Unknown"),
            ("The harder you work for something, the greater you’ll feel when you achieve it.", "Unknown"),
            ("Dream bigger. Do bigger.", "Unknown"),
            ("Don’t stop when you’re tired. Stop when you’re done.", "Unknown"),
            ("Wake up with determination. Go to bed with satisfaction.", "Unknown"),
            ("Do something today that your future self will thank you for.", "Unknown"),
            ("Little things make big days.", "Unknown"),
            ("It’s going to be hard, but hard does not mean impossible.", "Unknown"),
            ("Don’t wait for opportunity. Create it.", "Unknown"),
            ("Sometimes we’re tested not to show our weaknesses, but to discover our strengths.", "Unknown"),
            ("The key to success is to focus on goals, not obstacles.", "Unknown"),
            # Additional quotes
            ("Life is what happens when you're busy making other plans.", "John Lennon"),
            ("In three words I can sum up everything I've learned about life: it goes on.", "Robert Frost"),
            ("The greatest glory in living lies not in never falling, but in rising every time we fall.",
             "Nelson Mandela"),
            ("The way to get started is to quit talking and begin doing.", "Walt Disney"),
            ("Life is either a daring adventure or nothing at all.", "Helen Keller"),
            ("You only live once, but if you do it right, once is enough.", "Mae West"),
            ("The only impossible journey is the one you never begin.", "Tony Robbins"),
            ("Life is short, and it is up to you to make it sweet.", "Sarah Louise Delany"),
            ("The purpose of our lives is to be happy.", "Dalai Lama"),
            ("You don't have to be great to start, but you have to start to be great.", "Zig Ziglar"),
            ("Life is 10% what happens to us and 90% how we react to it.", "Charles R. Swindoll"),
            ("Opportunities don't happen, you create them.", "Chris Grosser"),
            ("You miss 100% of the shots you don't take.", "Wayne Gretzky"),
            ("Life is like riding a bicycle. To keep your balance, you must keep moving.", "Albert Einstein"),
            ("Success is not how high you have climbed, but how you make a positive difference to the world.",
             "Roy T. Bennett"),
            ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
            ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
            ("It's not the years in your life that count. It's the life in your years.", "Abraham Lincoln"),
            ("The only way to do great work is to love what you do.", "Steve Jobs"),
            ("Strive not to be a success, but rather to be of value.", "Albert Einstein"),
            ("You must be the change you wish to see in the world.", "Mahatma Gandhi")
        ]

        return random.choice(quotes)

    def notify_to_all(self, recipient_list):
        conn = self.main_connection()
        sender = "Do not reply. This email is autogenerated."
        host = conn['host']
        port = conn['port']
        username = conn['username']
        password = conn['password']

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        token = self.generate_token()

        self.write({'approval_link': token})

        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', self.task) if self.task else 'N/A'
        capitalized_sentences = [sentence.capitalize() for sentence in sentences]
        proper_text = ' '.join(capitalized_sentences)
        quote, author = self.generate_motivational_quote()

        result = 'N/A'

        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))

        msg['To'] = ', '.join(recipient_list)
        msg['Subject'] = (
            f"{str(self.form_request_type).title() if self.state else ''} "
            f"Request has been {str(self.state).title() if self.state else ''} "
            f"[{str(self.name)}]"
        )

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
                                            .header1 {
                                                text-align: center;
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
                                                border: 1px solid white;
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
                                                Hello <b>{self.requesters_id.name}</b> </br> Your Request: <b>{proper_text.title() if self.state else ''}</b> </br> Request has been <b>{re.sub(r'[-_]', ' ', self.state).title() if self.state else ''}</b> </br> Controll Number:  <b>[{self.name}]</b> </br>Priority Level: <b>{re.sub(r'[-_]', ' ', self.priority_level).title()}</b> </br> Workers: <b>{', '.join(self.get_workers()) if self.workers_assigned_when_changed else self.workers_requested} {result} </b>
                                                </div>
                                                <div class="header1">
                                                    </br></br>
                                                    </br></br>
                                                    </br></br>
                                                    </br></br>
                                                    </br></br>
                                                    </br></br>
                                                    </br></br>
                                                    </br></br>
                                                    </br></br>
                                                    </br></br>
                                                    </br></br>
                                                    </br></br>
                                                    </br></br>
                                                    </br></br>
                                                    <span style='font-size: 12px; margin-top: 50px; float: left;'>Quote for the Day - "<i>{quote} - {author}</i>"</span>
                                                </div>
                                            </div>
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

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('create.sequence.form.sequence.jrf') or '/'
        return super(JobRequest, self).create(vals)
