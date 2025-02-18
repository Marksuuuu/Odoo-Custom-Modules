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


class DexServiceRequestForm(models.Model):
    _name = 'dex_service.request.form'
    _description = 'Dex Service Request Form'
    _order = 'id desc'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Control No.',
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New'),
        tracking=True
    )

    status = fields.Selection(
        [('draft', 'Draft'), ('submitted', 'Submitted'), ('created', 'Created'), ('cancelled', 'Cancelled'), ],

        default='draft',
        string='Type')

    dex_service_request_form_line_ids = fields.One2many(
        'dex_service.request.form.line',
        'dex_service_request_form_id'
    )

    sales_coordinator = fields.Many2one('hr.employee', string='Sales Coordinator')

    partner_id = fields.Many2one(
        'res.partner',
        domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)],
        required=False,
        store=True
    )

    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    city = fields.Char(related='partner_id.city')
    state_id = fields.Many2one(related='partner_id.state_id')
    zip = fields.Char(related='partner_id.zip')
    country_id = fields.Many2one(related='partner_id.country_id')
    user_id = fields.Many2one(related='partner_id.user_id')
    type = fields.Selection(related='partner_id.type')
    service_type = fields.Many2one('dex_service.service.type', string='Service Type')

    what_type = fields.Selection(
        [('by_invoice', 'By Invoice'), ('by_warranty', 'By Warranty'),
         ('by_edp_code', 'By EDP-Code'),
         ('by_edp_code_not_existing', 'By EDP-Code (Not Existing)')],
        default=False,
        string='Type'
    )

    brand_units = fields.Many2one('uom.uom', string='Brand Units')
    number_of_units = fields.Integer(string='Number of Units')
    sale_order_no = fields.Many2one('sale.order', string='Sale Order')
    date_of_purchase = fields.Datetime(string='Date of Purchase')

    is_created = fields.Boolean(default=False)

    thread_id = fields.Many2one('dex_service.service.line.thread', string='Thread Id',
                                domain=[('status', '!=', 'close')])

    requesters_id = fields.Many2one(
        'hr.employee',
        string='Requesters',
        required=False,
        default=lambda self: self.env.user.employee_id.id,
        copy=False
    )

    department_id = fields.Many2one(related='requesters_id.department_id', string='Department')

    is_service_tech = fields.Boolean(default=False)

    date_called_by_client = fields.Datetime(string='Date Called by Client')
    trouble_reported = fields.Char(string='Trouble Reported')
    remarks = fields.Text(string='Remarks')

    time_in = fields.Float(string='Time In')
    time_out = fields.Float(string='Time Out')

    cancellation_reason = fields.Text(string="Reason for Cancellation")
    cancelled_by = fields.Many2one('res.users', string="Cancelled By")
    cancelled_date = fields.Datetime(string="Cancelled Date")
    is_cancelled = fields.Boolean(default=False)

    check_status = fields.Boolean(compute='_compute_check_status_is_cancelled', default=False, tracking=True)

    other_details = fields.Text(string='Other Details')

    html_content = fields.Html(
        string="HTML Content",
        default="""<table class="table table-bordered">
                       <thead>
                           <tr>
                               <th>Header 1</th>
                               <th>Header 2</th>
                           </tr>
                       </thead>
                       <tbody>
                           <tr>
                               <td>Row 1, Cell 1</td>
                               <td>Row 1, Cell 2</td>
                           </tr>
                           <tr>
                               <td>Row 2, Cell 1</td>
                               <td>Row 2, Cell 2</td>
                           </tr>
                       </tbody>
                   </table>""",
    )

    def cancel_request(self):
        pass

    @api.depends('status', 'check_status')
    def _compute_check_status_is_cancelled(self):
        mail_list = []
        if self.cancelled_by.login:
            mail_list.append(self.cancelled_by.login)
        if self.requesters_id:
            mail_list.append(self.requesters_id.work_email)
            mail_list.append('john.llavanes@dexterton.loc')
            mail_list.append('service@dexterton.loc')

        # Check if the request is cancelled
        if self.status == 'cancelled':
            self.check_status = True
            font_awesome = "fa fa-ban"
            self.notify_to_all(mail_list, font_awesome)
        else:
            self.check_status = False  # Reset check_status if not cancelled

    def get_emails_by_department(self):
        employee_emails = []
        employee_emails.append('service@dexterton.loc')
        employee_emails.append('john.llavanes@dexterton.loc')
        return employee_emails
        # department_name = 'Service Dept.'
        # department = self.env['hr.department'].sudo().search([('name', '=', department_name)], limit=1)
        #
        # if department:
        #     employees = self.env['hr.employee'].sudo().search([('department_id', '=', department.id)])
        #
        #     employee_emails = [employee.work_email for employee in employees if employee.work_email]
        #     employee_emails.append('john.llavanes@dexterton.loc')
        #
        #     return employee_emails
        # else:
        #     return f"No department found with name {department_name}"

    def main_connection(self):
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

    def notify_to_all(self, recipient_list, font_awesome):
        conn = self.main_connection()
        sender = "Do not reply. This email is autogenerated."
        host = conn['host']
        port = conn['port']
        username = conn['username']
        password = conn['password']

        # Prepare the email message
        msg = MIMEMultipart()
        msg['From'] = formataddr(('Service Mailer - Odoo', sender))
        msg['To'] = ', '.join(recipient_list)
        msg[

            'Subject'] = f'This Request with serial number of "[{self.name}]" has {"Cancelled" if self.is_cancelled else "Created"}'

        # HTML content
        html_content = """
            <!DOCTYPE html>
            <html lang="en">
              <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                <title>Responsive Services Section</title>
                <!-- Font Awesome CDN -->
                <link
                  rel="stylesheet"
                  href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
                />
                <!-- Google Font -->
                <link
                  href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap"
                  rel="stylesheet"
                />
                <!-- Stylesheet -->
                <style>
                  * {
                    padding: 0;
                    margin: 0;
                    box-sizing: border-box;
                    font-family: "Poppins", sans-serif;
                  }
                  section {
                    height: 100vh;
                    width: 100%;
                    display: grid;
                    place-items: center;
                  }
                  .container {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 1em;
                    padding: 1em;
                    max-width: 1200px;
                    width: 100%;
                  }
                  .card {
                    flex: 1 1 100%;
                    max-width: 100%;
                    padding: 2em 1.5em;
                    background: linear-gradient(#ffffff 50%, #2c7bfe 50%);
                    background-size: 100% 200%;
                    background-position: 0 2.5%;
                    border-radius: 5px;
                    box-shadow: 0 0 35px rgba(0, 0, 0, 0.12);
                    cursor: pointer;
                    transition: 0.5s;
                  }
                  h3 {
                    font-size: 20px;
                    font-weight: 600;
                    color: #1f194c;
                    margin: 1em 0;
                  }
                  p {
                    color: #575a7b;
                    font-size: 15px;
                    line-height: 1.6;
                    letter-spacing: 0.03em;
                  }
                  .icon-wrapper {
                    background-color: #2c7bfe;
                    position: relative;
                    margin: auto;
                    font-size: 30px;
                    height: 2.5em;
                    width: 2.5em;
                    color: #ffffff;
                    border-radius: 50%;
                    display: grid;
                    place-items: center;
                    transition: 0.5s;
                  }
                  .card:hover {
                    background-position: 0 100%;
                  }
                  .card:hover .icon-wrapper {
                    background-color: #ffffff;
                    color: #2c7bfe;
                  }
                  .card:hover h3 {
                    color: #ffffff;
                  }
                  .card:hover p {
                    color: #f0f0f0;
                  }
                  table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 1em;
                  }
                  th, td {
                    padding: 0.75em;
                    border: 1px solid #dddddd;
                    text-align: left;
                  }
                  th {
                    background-color: #f4f4f4;
                  }
                  tr:nth-child(even) {
                    background-color: #f9f9f9;
                  }
                  /* @media screen and (min-width: 768px) {
                    .card {
                      flex: 0 0 50%;
                    }
                  }
                  @media screen and (min-width: 992px) {
                    .card {
                      flex: 0 0 33.33%;
                    }
                  } */
                </style>
              </head>"""
        html_content += f"""
              <body>
                <section>
                  <div class="container">
                    <div class="card">
                      <div class="icon-wrapper">
                        <i class="{font_awesome}"></i>
                      </div>
                        <h3>Service Control Number: {'[' + self.name + ']' if self.name else ''}</h3>
                        <h3>Created by: {'[' + self.requesters_id.name + ']' if self.requesters_id else ''}</h3>
                        <h3>{'' if self.is_cancelled else f"Trouble Reported: {'[' + self.trouble_reported + ']' if self.trouble_reported else ''}"}</h3>
                        <h3>{'' if self.is_cancelled else f"Date Called: {'[' + str(self.date_called_by_client) + ']' if self.date_called_by_client else ''}"}</h3>

                        <h3>{f"Cancelled by : {'[' + self.cancelled_by.name + ']' if self.cancelled_by else ''}" if self.cancelled_by else ''}</h3>
                        <h3>{f"Cancelled date : {'[' + str(self.cancelled_date) + ']' if self.cancelled_date else ''}" if self.cancelled_date else ''}</h3>
                        <h3>{f"Cancelled reason : {'[' + str(self.cancellation_reason) + ']' if self.cancellation_reason else ''}" if self.cancellation_reason else ''}</h3>

                        <p>{f"Other Details : {'[' + str(self.other_details) + ']' if self.other_details else ''}" if self.is_cancelled else ''}</p>

                    <table>
                        <thead>
                          <tr>
                            <th>Edp Code</th>
                            <th>Description</th>
                            <th>Brand</th>
                          </tr>
                        </thead>
                        <tbody>"""
        for rec in self.dex_service_request_form_line_ids:
            html_content += f"""
                        <tr>
                            <td>{rec.edp_code.default_code if rec.edp_code else ''}</td>
                            <td>{rec.description if rec.description else ''}</td>
                            <td>{rec.brand_id.name if rec.brand_id else ''}</td>
                        </tr>
                            """

        html_content += """
                        </tbody>
                      </table>
                    </div>
                  </div>
                </section>
              </body>
            </html>
        """
        msg.attach(MIMEText(html_content, 'html'))

        try:
            smtpObj = smtplib.SMTP(host, port)
            smtpObj.login(username, password)
            # new_recipient = 'john.llavanes@dexterton.loc'
            # recipient_list += [new_recipient]
            smtpObj.sendmail(sender, recipient_list, msg.as_string())
            smtpObj.quit()

            msg = "Successfully sent email"
            _logger.info('msg {}'.format(msg))
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'type': 'success',
                    'message': msg,
                    'sticky': False,
                }
            }
            return notification
        except Exception as e:
            msg = f"Error: Unable to send email: {str(e)}"
            _logger.info('msg {}'.format(msg))
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'type': 'error',
                    'message': msg,
                    'sticky': False,
                }
            }

            return notification

    def submit(self):
        self.status = 'submitted'
        font_awesome = "fa fa-bell"
        email = self.get_emails_by_department()
        _logger.info('testtttttttt {}'.format(email))
        # email = 'john.llavanes@dexterton.loc'
        self.notify_to_all(email, font_awesome)

    @api.onchange('requesters_id')
    def onchange_requesters_id(self):
        if self.requesters_id:
            job_name = self.requesters_id.job_id.sudo().name
            self.is_service_tech = job_name == 'Service Technician'

    @api.onchange('thread_id')
    def onchange_thread_id(self):
        if self.thread_id and self.thread_id.client_name:
            self.partner_id = self.thread_id.client_name.id
            prod_name = self.thread_id.item_description

            prod_template = self.env['product.template'].search([('name', '=', prod_name)])
            if prod_template:
                self.dex_service_request_form_line_ids = [(5, 0, 0)]

                vals_list = []
                for line_id in self.thread_id:
                    vals = {
                        'edp_code': prod_template.id,
                    }
                    vals_list.append((0, 0, vals))
                self.dex_service_request_form_line_ids = vals_list
            else:
                _logger.warning('Product template not found for name: {}'.format(prod_name))

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('dex.service.form.sequence.sfs') or '/'
        return super(DexServiceRequestForm, self).create(vals)

    @api.model
    def find_or_create_record(self, search_criteria, default_values):
        existing_records = self.env['service'].search(search_criteria)
        service_line_ids = default_values.pop('service_line_ids', [])
        search_existing_records_thread = False
        if self.thread_id:
            search_existing_records_thread = self.env['dex_service.service.line.thread'].search([
                ('id', '=', self.thread_id.id)
            ])
            search_existing_records_time = self.env['dex_service.assign.request.service.time'].search([
                ('service_id', '=', self.thread_id.id)
            ])
            search_existing_records_line = self.env['dex_service.assign.request.line'].search([
                ('service_id', '=', self.thread_id.id)
            ])
            search_existing_records_details = self.env['dex_service.assign.request.other.details'].search([
                ('service_id', '=', self.thread_id.id)
            ])

        for line in service_line_ids:
            if not (isinstance(line, tuple) and len(line) == 3):
                _logger.error('Unexpected line format: {}'.format(line))
                continue

            operation_type, _, line_data = line
            if isinstance(line_data, dict):
                filtered_line = {
                    'client_name': line_data.get('client_name'),
                    'item_description': line_data.get('item_description'),
                    'edp_code': line_data.get('edp_code'),
                    'requested_by': line_data.get('requested_by'),
                    'trouble_reported': line_data.get('trouble_reported'),
                    'brand_id': line_data.get('brand_id'),
                }

                if search_existing_records_thread and search_existing_records_time and search_existing_records_line and search_existing_records_details:
                    try:
                        search_existing_records_thread.write(filtered_line)
                        search_existing_records_line.write({
                            # 'brand_id': line_data.get('edp_code'),
                        })
                        search_existing_records_details.write({
                            'trouble_reported': line_data.get('trouble_reported'),
                            'remarks': line_data.get('remarks'),
                            'call_date': line_data.get('call_date')
                        })
                        search_existing_records_time.write({
                            'time_in': line_data.get('time_in'),
                            'time_out': line_data.get('time_out'),
                        })
                    except Exception as e:
                        _logger.error('Failed to write to thread: {}'.format(e))

        if existing_records:
            for record in existing_records:
                record.write(default_values)
            records = existing_records
            for line in service_line_ids:
                operation_type, _, line_data = line
                filtered_line = {
                    'client_name': line_data.get('client_name'),
                    'item_description': line_data.get('item_description'),
                    'requested_by': line_data.get('requested_by'),
                    'service_id': existing_records.id,
                    'edp_code': line_data.get('edp_code'),
                    'brand_id': line_data.get('brand_id'),
                }
                records.service_line_ids.create(filtered_line)
        else:
            record = self.env['service'].create(default_values)
            records = self.env['service'].browse(record.id)
            for line in service_line_ids:
                operation_type, _, line_data = line
                filtered_line = {
                    'client_name': line_data.get('client_name'),
                    'item_description': line_data.get('item_description'),
                    'requested_by': line_data.get('requested_by'),
                    'service_id': records.id,
                    'edp_code': line_data.get('edp_code'),
                    'brand_id': line_data.get('brand_id'),

                }
                records.service_line_ids.create(filtered_line)

    def action_find_or_create(self):
        search_criteria = [('partner_id', '=', self.partner_id.id)]
        service_line_ids = self.dex_service_request_form_line_ids

        default_values = {
            'partner_id': self.partner_id.id,
            'service_line_ids': [(0, 0, {
                'call_date': self.date_called_by_client,
                'client_name': self.partner_id.id,
                'requested_by': self.requesters_id.name,
                'item_description': line.description,
                'edp_code': line.edp_code.id,
                'brand_id': line.brand_id.id,
                'remarks': self.remarks,
                'time_in': self.time_in,
                'time_out': self.time_out,
                'trouble_reported': self.trouble_reported,
            }) for line in service_line_ids]
        }
        self.is_created = True
        self.status = 'created'
        return self.find_or_create_record(search_criteria, default_values)


class DexServiceRequestFormLine(models.Model):
    _name = 'dex_service.request.form.line'
    _description = 'Dex Service Request Form Line'

    dex_service_request_form_id = fields.Many2one(
        'dex_service.request.form',
        string='Service Request Form'
    )

    edp_code = fields.Many2one(
        'product.template',
        string='EDP-Code',
        domain=[('default_code', '!=', False)]
    )

    description = fields.Char(related='edp_code.name')

    brand_id = fields.Many2one(related='edp_code.brand_id')
