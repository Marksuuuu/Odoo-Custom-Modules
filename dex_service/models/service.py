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


class Service(models.Model):
    _name = 'service'
    _description = 'Dex Service'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    _order = 'id desc'
    

    name = fields.Char(string='Control No.', copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), tracking=True)

    service_line_ids = fields.One2many('service.line', 'service_id')
    
    sales_coordinator = fields.Many2one('hr.employee', string='Sales Coordinator')
    
    daily_sales_report_date = fields.Datetime(string='Daily Sales Report', default=fields.Datetime.now)


    partner_id = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)], required=True)
    

    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    city = fields.Char(related='partner_id.city')
    state_id = fields.Many2one(related='partner_id.state_id')
    zip = fields.Char(related='partner_id.zip')
    country_id = fields.Many2one(related='partner_id.country_id')
    user_id = fields.Many2one(related='partner_id.user_id')
    type = fields.Selection(related='partner_id.type')
    service_type = fields.Many2one('service.type', string='Service Type')
    
    transfer_to_partner_id = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)])
    transfer_to_street = fields.Char(related='transfer_to_partner_id.street')
    transfer_to_street2 = fields.Char(related='transfer_to_partner_id.street2')
    transfer_to_city = fields.Char(related='transfer_to_partner_id.city')
    transfer_to_state_id = fields.Many2one(related='transfer_to_partner_id.state_id')
    transfer_to_zip = fields.Char(related='transfer_to_partner_id.zip')
    transfer_to_country_id = fields.Many2one(related='transfer_to_partner_id.country_id')
    transfer_to_type = fields.Selection(related='transfer_to_partner_id.type')
    transfer_to_user_id = fields.Many2one(related='transfer_to_partner_id.user_id')

    what_type = fields.Selection(
        [('by_invoice', 'By Invoice'), ('by_warranty', 'By Warranty'), ('by_edp_code', 'By EDP-Code'),('by_edp_code_not_existing', 'By EDP-Code (Not Existing)')], default=False,
        string='Type')
    
    is_client_blocked = fields.Boolean(default=False)
    
    block_reason = fields.Char(string='Block Reason')
    
    is_tranfered = fields.Boolean(default=False)
    transfer_reason = fields.Char(string='Transfer Reason')
    
    requesters_id = fields.Many2one('res.users', string='Requester', default=lambda self: self.env.user.id)
    
    count_service_line_ids = fields.Integer(string='Line Count', compute='_compute_service_line_ids')
    


    
    def open_form_view(self):
        pass
    
    @api.depends('count_service_line_ids')
    def _compute_service_line_ids(self):
        for record in self:
            record.count_service_line_ids = len(record.service_line_ids)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('create.sequence.form.sequence.srf') or '/'
        
        return super(Service, self).create(vals)

    def action_client_search(self):
        action = self.with_context(bypass_partner_validation=True).client_search()
        return action
    
    def client_search(self):
        action = {
            'name': 'Client Search',
            'type': 'ir.actions.act_window',
            'res_model': 'client.search',
            'view_mode': 'form',
            'target': 'new',
            'domain': [],
            'context': { }
        }
        return action

    def by_invoice(self):
        request_type = 1
        action = self.create_ticket_by(request_type, 'By Invoice', what_type='by_invoice')
        return action

    def by_warranty(self):
        request_type = 2
        action = self.create_ticket_by(request_type, 'By Warranty', what_type='by_warranty')
        return action

    def by_edp_code(self):
        request_type = 3
        action = self.create_ticket_by(request_type, 'By EDP-Code', what_type='by_edp_code')
        return action
    
    def by_edp_code_not_existing(self):
        request_type = 4
        action = self.create_ticket_by(request_type, 'By EDP-Code (Not Existing)', what_type='by_edp_code_not_existing')
        return action
    
    def create_so(self):
        if self.is_client_blocked == True:
            raise UserError("Can't Proceed This Service Blocked.. Please Unblock First!.")
        else:
            action = {
                'name': 'Create SO',
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'form',
                'target': 'new',
                'domain': [],
                'context': {
                    'default_service_id': self.id,
                    'default_partner_id': self.partner_id.id,
                    'default_what_type': self.what_type,
    
                }
            }
            return action
    
    def block_client(self):
        action = {
            'name': 'Block Client?',
            'type': 'ir.actions.act_window',
            'res_model': 'block.reason',
            'view_mode': 'form',
            'target': 'new',
            'domain': [],
            'context': {
                'default_service_id': self.id,
            }
        }
        return action
    
    def unblock_client(self):
        _logger.info('Un Blocked')
        self.is_client_blocked = False
        self.block_reason = False

    def create_ticket_by(self, request_type, type, what_type):
        action = {
            'name': f'Create Ticket {type}',
            'type': 'ir.actions.act_window',
            'res_model': 'create.ticket.by',
            'view_mode': 'form',
            'target': 'new',
            'domain': [],
            'context': {
                'default_service_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_what_type': what_type,
                'default_request_type': request_type,

            }
        }
        return action
    
    def transfer_to(self):
        action = {
            'name': 'Transfer Client',
            'type': 'ir.actions.act_window',
            'res_model': 'transfer.to',
            'view_mode': 'form',
            'target': 'new',
            'domain': [],
            'context': {
                'default_service': self.id,
                'default_partner_id': self.partner_id.id,

            }
        }
        return action
    

    

class ServiceLine(models.Model):
    _name = 'service.line'
    _order = 'id desc'
    _rec_name = 'name'
    _description = 'Dex Service Line'

    service_id = fields.Many2one('service', string='Service Id', ondelete='cascade')
    name = fields.Char(string='Control No.', copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), tracking=True)
    status = fields.Selection(
        [('open', 'Open'), ('cancelled', 'Cancelled'),('close', 'Close'), ('pending', 'Pending'), ('waiting', 'Waiting')], default='open',
        string='Type')

    invoice_id = fields.Many2one('account.move', string='Invoice ID')
    purchase_date = fields.Date(string='Purchase Date')
    with_warranty = fields.Boolean(default=False)
    warranty_number = fields.Many2one('warranty', string='Warranty #')
    serial_number = fields.Char(string='Serial #')
    item_description = fields.Char(string='Item Description')
    client_name = fields.Many2one('res.partner', domain=[('type', '=', 'invoice'), ('customer_rank', '>', 1)], store=True)

    service_type = fields.Many2one('service.type', string='Service Type', store=True)
    complaints = fields.Char(string='Complaints')
    feedback_count = fields.Integer(string='Feedback Count')

    street = fields.Char(related='client_name.street')
    street2 = fields.Char(related='client_name.street2')
    city = fields.Char(related='client_name.city')
    state_id = fields.Many2one(related='client_name.state_id')
    zip = fields.Char(related='client_name.zip')
    country_id = fields.Many2one(related='client_name.country_id')
    user_id = fields.Many2one(related='client_name.user_id')

    call_date = fields.Datetime(string='Call Date')
    requested_by = fields.Char(string='Requested by')
    phone_number = fields.Integer(string='Phone #')
    look_for = fields.Char(string='Look For')
    charge = fields.Float(string='Charge')
    free_of_charge = fields.Boolean(string='Free of Charge?')
    
    what_type = fields.Selection(
        [('by_invoice', 'By Invoice'), ('by_warranty', 'By Warranty'), ('by_edp_code', 'By EDP-Code'),('by_edp_code_not_existing', 'By EDP-Code (Not Existing)')], default=False,
        string='Type')

    tentative_schedule_date = fields.Date(string='Tentative Schedule Date')

    other_instructions = fields.Char(string='Other Instructions')

    pending_reason = fields.Char(string='Pending Reason', default=False)

    thread_count = fields.Integer(string='Thread Count')

    count_field = fields.Integer(default=30)
    
    is_tentative_date_added = fields.Boolean(
        default=False, 
        compute='_check_tentative_date', 
        store=True
    )
    requesters_id = fields.Many2one('res.users', string='Requester', default=lambda self: self.env.user.id)
    
    checking_status = fields.Boolean(default=False, compute='_compute_checking_status')
    
    pending_date = fields.Datetime(string="Pending Date")
    done_date = fields.Datetime(string="Done Date")
    total_duration = fields.Float(string="Total Duration (hours)", readonly=True)
    actual_duration = fields.Float(string="Actual Duration (hours)", compute='_compute_actual_duration', store=False)
    
    is_inputs_complete = fields.Boolean(default=False, compute='_compute_check_if_complete')

    
    @api.depends('tentative_schedule_date', 'complaints', 'phone_number')
    def _compute_check_if_complete(self):
        for record in self:
            record.is_inputs_complete = bool(record.tentative_schedule_date or record.complaints or record.phone_number)
            
    def print_service_request_form(self):
        return self.env.ref('dex_service.service_request_form_report_id').report_action(self)

    @api.model
    def write(self, vals):
        if 'status' in vals:
            if vals['status'] == 'pending':
                vals['pending_date'] = datetime.now()
                vals['done_date'] = False  # Reset done date if going back to pending

            elif vals['status'] == 'done' and self.pending_date:
                vals['done_date'] = datetime.now()
                # Calculate total duration
                duration = vals['done_date'] - self.pending_date
                vals['total_duration'] = duration.total_seconds() / 3600  # Convert to hours

        return super(ServiceLine, self).write(vals)

    @api.depends('pending_date')
    def _compute_actual_duration(self):
        for record in self:
            if record.pending_date:
                current_time = datetime.now()
                duration = current_time - record.pending_date
                record.actual_duration = duration.total_seconds() / 3600  # Convert to hours
            else:
                record.actual_duration = 0.0  # Reset if pending_date is not set
    
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
    
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('create.service.request.sequence.srs') or '/'
        return super(ServiceLine, self).create(vals)
    
    def check_count_of_report_print_count(self):
        search_for_assign_request = self.env['assign.request'].search([('service_id', '=', self.id)])
        # total_count = 0  
        # for rec in self:
        #     total_count += rec.report_print_count  
        # return total_count
    
    
    def assign_workers(self):
        for record in self:
            record_id = record.id
            view_id = self.env.ref('dex_service.assign_request_dex_service_action').id
            action = {
                'name': 'Assign Workers',
                'type': 'ir.actions.act_window',
                'res_model': 'assign.request',
                'view_mode': 'tree,form',
                # 'view_id': view_id,
                'target': 'current',
                'domain': [('service_id', '=', record_id)],
                'context': {
                    'default_service_id': record_id,
                    'default_call_date': self.call_date,
                    'default_look_for': self.look_for,
                    'default_assign_request_line_ids': [(0, 0, {'partner_id': self.client_name.id, 'look_for': self.look_for})],
                    'default_assign_request_service_time_ids': [(0, 0, {'partner_id': self.client_name.id, 'parts_cost_actual': self.charge})],
                    'default_assign_request_other_details_ids': [(0, 0, {'partner_id': self.client_name.id})]

                }
            }
            return action
    
    

    def show_thread(self):
        for record in self:
            record_id = record.id
            action = {
                'name': 'Create Thread',
                'type': 'ir.actions.act_window',
                'res_model': 'service.line.thread',
                'view_mode': 'tree,form',
                'target': 'current',
                'domain': [('service_line_main_ids', '=', record_id)],
                'context': {
                    'default_service_line_main_ids': record_id,
                    'default_client_name': self.client_name.id,
                    'default_call_date': self.call_date,
                    # 'default_look_for': self.look_for


                }
            }
            return action

    def create_thread(self):
        for record in self:
            record_id = record.id
            # view_id = self.env.ref('dex_service.create_thread_wizard').id
            action = {
                'name': 'Create Thread',
                'type': 'ir.actions.act_window',
                'res_model': 'create.thread.wizard',
                # 'views': [(view_id, 'form')],
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_status': self.status,
                    'default_service_line_main_ids': record_id,
                    'default_client_name': self.client_name.id,
                    'default_invoice_id': self.invoice_id.id,
                    'default_purchase_date': self.purchase_date,
                    'default_item_description': self.item_description,
                    'default_service_type': self.service_type.id,
                    'default_call_date': self.call_date,
                    'default_look_for': self.look_for




                }
            }
            return action
        
    @api.depends('status')
    def _compute_checking_status(self):
        for record in self:
            if not record.pending_reason:
                record.checking_status = False
            else:
                from_what = 2
                email_recipients = [record.requesters_id.login]
                font_awesome = 'fa-solid fa-clock'
                # Uncomment if check_and_send_email is implemented
                # record.check_and_send_email(email_recipients, from_what, font_awesome)
                record.checking_status = True
            
        
    @api.model
    def get_all_partner_ids(self):
        partner_ids = set()
        if self.client_name:
            partner_ids.add(self.client_name.email)
        if not self.id:
            return list(partner_ids)
        assign_requests = self.service_id.search([('service_line_ids', '=', self.id)])
        for request in assign_requests:
            for line in request.service_line_ids:
                if line.partner_id:
                    partner_ids.add(line.partner_id.email)
        return list(partner_ids)

    @api.onchange('status', 'pending_reason')
    def onchange_status(self):
        partner_ids = self.get_all_partner_ids()
        email_recipients = [self.requesters_id.login]
        
        if self.user_id:
            user_login = self.user_id.login
            if user_login:
                partner_ids.append(user_login)
            
        from_what = 2
        if self.status == 'open':
            font_awesome = 'fa-solid fa-door-open'
            self.notify_to_all(email_recipients, from_what, font_awesome)
        elif self.status == 'cancelled':
            font_awesome = 'fa-solid fa-xmark'
            self.notify_to_all(email_recipients, from_what, font_awesome)
        elif self.status == 'close':
            font_awesome = 'fa-solid fa-door-closed'
            self.notify_to_all(email_recipients, from_what, font_awesome)
        elif self.status == 'pending':
            if self.pending_reason:
                
                font_awesome = 'fa-solid fa-clock'
                self.notify_to_all(email_recipients, from_what, font_awesome)
            # self.check_and_send_email(email_recipients, from_what, font_awesome)
        elif self.status == 'waiting':
            font_awesome = 'fa-solid fa-hourglass-start'
            self.notify_to_all(email_recipients, from_what, font_awesome)
        else:
            'fa-solid fa-bug'
    
    # def check_and_send_email(self, email_recipients, from_what, font_awesome):
    #     _logger.info('pending_here1')
    #     
    #     if self.status == 'pending' and self.pending_reason is not False:
    #         _logger.info('pending_here2')
    #         self.notify_to_all(email_recipients, from_what, font_awesome)
    #         _logger.info('Notification sent to all partners due to pending status.')

  
    @api.depends('tentative_schedule_date')
    def _check_tentative_date(self):
        for record in self:
            if record.tentative_schedule_date:
                record.is_tentative_date_added = True
                sales_person = self.get_email_sales_person()
                create_by = self.get_email_create_by()
                email_recipients = [sales_person if sales_person else '', create_by if create_by else '']
                _logger.info('email_recipients {}'.format(email_recipients))
                from_what = 1
                font_awesome = 'fa-solid fa-calendar-days'
                record.notify_to_all(email_recipients, from_what, font_awesome)
            else:
                # record.send_email_to()
                record.is_tentative_date_added = False
      
    def get_email_sales_person(self):
        email = self.user_id.login
        return email
    
    def get_email_create_by(self):
        email = self.requesters_id.login
        return email
    
    # def send_email_to(self):
    #     sales_person = self.get_email_sales_person()
    #     create_by = self.get_email_create_by()
    #     email_recipients = [sales_person, create_by]
    #     from_what = 1
    #     font_awesome = 'fa-solid fa-calendar-days'
    #     self.notify_to_all(email_recipients, from_what, font_awesome)
        
    def notify_to_all(self, recipient_list, from_what, font_awesome):
        conn = self.main_connection()
        sender = "Do not reply. This email is autogenerated."
        host = conn['host']
        port = conn['port']
        username = conn['username']
        password = conn['password']
    
        if from_what == 1:
            title_format = f'This Request with serial number of "[{self.name}]" have an Tentative Date'
        elif from_what == 2:
            title_format = f'This Request with serial number of "[{self.name}]" have Change the STATUS [{self.status.title() if self.status else ""}]'
        else:
            title_format = ''
    
        # Prepare the email message
        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))
        msg['To'] = ', '.join(recipient_list)
        msg['Subject'] = title_format
    
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
                      <h3>Service Control Number {'[' + self.name + ']' if self.name else ''}</h3>
                      <table>
                        <thead>
                          <tr>
                            <th>#</th>
                            <th>Client Name</th>
                            <th>Service Type</th>
                            <th>Tentative Schedule Date</th>
                            <th>Item Description</th>
                            <th>Sales Person</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td>1</td>
                            <td>{self.client_name.name if self.client_name else 'N/A'}</td>
                            <td>{self.service_type.name if self.service_type else 'N/A'}</td>
                            <td>{self.tentative_schedule_date.strftime("%m-%d-%y") if self.tentative_schedule_date else 'N/A'}</td>
                            <td>{self.item_description if self.item_description else 'N/A'}</td>
                            <td>{self.user_id.name if self.user_id else 'N/A'}</td>
                          </tr>
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
            smtpObj.sendmail(sender, recipient_list, msg.as_string())
            smtpObj.quit()
    
            msg = "Successfully sent email"
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

        
        
