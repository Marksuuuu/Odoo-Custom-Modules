from datetime import date, datetime
import hashlib
import re
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import openpyxl
from openpyxl.chart import BarChart, Reference
from io import BytesIO

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import formataddr
import json
import random

import logging

_logger = logging.getLogger(__name__)

class ServiceItineraryCron(models.Model):
    _inherit = 'assign.request'
    
    @api.model
    def _get_all_email(self):
        email_configs = self.env['itinerary.configuration'].search([])
        assign_requests = self.env['assign.request'].search([])
        email_list = []
        request_list = []
    
        for rec in email_configs:
            selected_data = dict(rec._fields['email_groups'].selection).get(rec.email_groups, '')
    
            if selected_data != 'Specific Email':
                email_list.append(rec.email_groups)
            elif selected_data == 'Specific Email':
                email_list.append(rec.specific_email)
    
        _logger.info('email_list {}'.format(email_list))
    
        # Collect emails from assign_requests
        for request in assign_requests:
            request_list.append(request)
        self.notify_to_all(email_list, assign_requests)
        _logger.info('request_list {}'.format(request_list))
    
        return email_list

    
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
    
    def notify_to_all(self, recipient_list, assign_requests):
        _logger.info('assign_request {}'.format(assign_requests))
        conn = self.main_connection()
        sender = "Do not reply. This email is autogenerated."
        host = conn['host']
        port = conn['port']
        username = conn['username']
        password = conn['password']
    
        # Prepare the email message
        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))
        msg['To'] = ', '.join(recipient_list)
        msg['Subject'] = 'Service Itinerary'
    
        # HTML content
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Service Itinerary</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f9f9f9;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                th, td {
                    padding: 12px;
                    text-align: left;
                    border: 1px solid #ddd;
                }
                th {
                    background-color: #0068AD;
                    color: white;
                }
                tr:hover {
                    background-color: #f1f1f1;
                }
            </style>
        </head>
        <body>
            <h2>Sample Table</h2>
            <table>
                <thead>
                    <tr>
                        <th>SERV. BY</th>
                        <th>CUSTOMER NAME</th>
                        <th>DATE PURCHASE</th>
                        <th>AREA</th>
                        <th>WARRANTY</th>
                        <th>AMOUNT</th>
                        <th>REMARKS</th>
                        <th>SERVICE TYPE</th>
                    </tr>
                </thead>
                <tbody>"""
        
        # Loop through each assign_request
        for assign_request in assign_requests:
            for line_id, service_time, other_detail in zip(assign_request.assign_request_line_ids,
                                                           assign_request.assign_request_service_time_ids,
                                                           assign_request.assign_request_other_details_ids):
                for technician in assign_request.technician:
                    _logger.info('other_detail.service_type.name {}'.format(other_detail.service_type.name))
                    html_content += f"""
                    <tr>
                        <td>{technician.name}</td>
                        <td>{line_id.partner_id.name}</td>
                        <td>{other_detail.purchase_date or 'N/A'}</td>
                        <td>{line_id.street + ' ' + line_id.city}</td>
                        <td>{'YES' if other_detail.with_warranty else 'NO'}</td>
                        <td>{'6969696969696'}</td>
                        <td>{other_detail.remarks if other_detail.remarks else ''}</td>
                        <td>{other_detail.service_type.name}</td>
                    </tr>"""
        
        # Close HTML content
        html_content += """
            </tbody>
        </table>
        </body>
        </html>"""
        
        msg.attach(MIMEText(html_content, 'html'))
        
        # Create XLSX file
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Service Itinerary"
        
        # Add headers
        headers = ['SERV. BY', 'CUSTOMER NAME', 'DATE PURCHASE', 'AREA', 'WARRANTY', 'AMOUNT', 'REMARKS', 'SERVICE TYPE']
        sheet.append(headers)
        
        # Add data
        for assign_request in assign_requests:
            for line_id, service_time, other_detail in zip(assign_request.assign_request_line_ids,
                                                           assign_request.assign_request_service_time_ids,
                                                           assign_request.assign_request_other_details_ids):
                for technician in assign_request.technician:
                    
                    sheet.append([
                        technician.name,
                        line_id.partner_id.name,
                        other_detail.purchase_date or 'N/A',
                        line_id.street + ' ' + line_id.city,
                        'YES' if other_detail.with_warranty else 'NO',
                        '6969696969696',
                        other_detail.remarks,
                        other_detail.service_type.name,
                    ])
        
        # Create a summary sheet for graphs
        summary_sheet = workbook.create_sheet(title="Summary")
        
        # Gather data for chart
        request_counts = {}
        for assign_request in assign_requests:
            for line_id in assign_request.assign_request_line_ids:
                for technician in assign_request.technician:
                    partner_name = line_id.partner_id.name
                    technician_name = technician.name
                    key = f"{partner_name} - {technician_name}"
                    if key not in request_counts:
                        request_counts[key] = 0
                    request_counts[key] += 1
        
        # Write summary data
        summary_sheet.append(['Partner - Technician', 'Requests'])
        for key, count in request_counts.items():
            summary_sheet.append([key, count])
        
        # Create a bar chart
        chart = BarChart()
        chart.title = "Requests per Partner and Technician"
        chart.x_axis.title = "Partner - Technician"
        chart.y_axis.title = "Number of Requests"
        
        # Reference for data
        data = Reference(summary_sheet, min_col=2, min_row=1, max_row=len(request_counts) + 1, max_col=2)
        categories = Reference(summary_sheet, min_col=1, min_row=2, max_row=len(request_counts) + 1)
        
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(categories)
        
        # Add the chart to the summary sheet
        summary_sheet.add_chart(chart, "E5")  # Position the chart at E5
        
        # Save to BytesIO
        excel_stream = BytesIO()
        workbook.save(excel_stream)
        excel_stream.seek(0)
        
        # Attach XLSX to the email
        xlsx_attachment = MIMEBase('application', 'octet-stream')
        xlsx_attachment.set_payload(excel_stream.read())
        encoders.encode_base64(xlsx_attachment)
        xlsx_attachment.add_header('Content-Disposition', 'attachment', filename='service_itinerary.xlsx')
        msg.attach(xlsx_attachment)
        
        try:
            smtpObj = smtplib.SMTP(host, port)
            smtpObj.login(username, password)
            smtpObj.sendmail(sender, recipient_list, msg.as_string())
            smtpObj.quit()
        
            msg = "Successfully sent email"
            _logger.info(msg)
        except Exception as e:
            msg = f"Error: Unable to send email: {str(e)}"
            _logger.info(msg)