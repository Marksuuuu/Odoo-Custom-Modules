import hashlib
import re
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

# from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ApprovalFieldsPlugin(models.AbstractModel):
    _name = 'approval.fields.plugins'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Approval Fields Plugin for Abstract Models'

    def _get_department_domain(self):
        return []

    def _get_default_currency_id(self):
        return self.env.company.currency_id.id

    @api.model
    def _get_default_journal(self):
        context = self._context
        company_id = context.get('force_company', context.get('default_company_id', self.env.company.id))
        journal_id = context.get('default_journal_id')

        move_type = context.get('default_type', 'in_invoice')
        sale_types = self.get_sale_types(include_receipts=True)
        purchase_types = self.get_purchase_types(include_receipts=True)

        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
            if move_type != 'in_invoice' and journal.type != ('sale' if move_type in sale_types else 'purchase'):
                raise UserError(_("Cannot create an invoice of type %s with a journal having %s as type.") % (
                    move_type, journal.type))
        else:
            journal_type = 'general'
            if move_type in sale_types:
                journal_type = 'sale'
            elif move_type in purchase_types:
                journal_type = 'purchase'

            domain = [('company_id', '=', company_id), ('type', '=', journal_type)]
            if context.get('default_currency_id'):
                domain += [('currency_id', '=', context['default_currency_id'])]

            journal = self.env['account.journal'].search(domain, limit=1)
            if not journal:
                error_msg = _('Please define an accounting %s journal in your company') % (
                    'miscellaneous' if journal_type == 'general' else journal_type)
                raise UserError(error_msg)

        return journal

    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 store=True, readonly=True,
                                 compute='_compute_company_id')

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 domain="[('company_id', '=', company_id)]",
                                 default=_get_default_journal)

    currency_id = fields.Many2one('res.currency', default=_get_default_currency_id)



    type = fields.Selection(selection=[
        ('entry', 'Journal Entry'),
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
        ('in_invoice', 'Vendor Bill'),
        ('in_refund', 'Vendor Credit Note'),
        ('out_receipt', 'Sales Receipt'),
        ('in_receipt', 'Purchase Receipt'),
    ], string='Type', required=True, store=True, index=True, readonly=True,
        default="entry", change_default=True)

    name = fields.Char(string='Control No.', copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    requesters_id = fields.Many2one('hr.employee', string='Requesters', required=True,
                                    default=lambda self: self.env.user.employee_id.id)
    requesters_email = fields.Char(related='requesters_id.work_email', string='Requesters Email', store=True)
    requesters_department = fields.Many2one(related='requesters_id.department_id', string='Requesters Department',
                                            store=True, required=False)

    # to be overridden by child models

    department_id = fields.Many2one('approver.setup', string='Department', domain=lambda a: a._get_department_domain(),
                                    tracking=True, required=True)

    form_request_type = fields.Selection(related='department_id.approval_type', string='Form Request Type', store=True,
                                         readonly=True)

    approval_stage = fields.Integer(default=1)
    approval_link = fields.Char(string='Approval Link')

    state = fields.Selection(
        selection=[('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'),
                   ('disapprove', 'Disapproved'), ('cancel', 'Cancelled')],
        default='draft')

    approval_status = fields.Selection(
        selection=[('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'),
                   ('disapprove', 'Disapproved'), ('cancel', 'Cancelled')], string='Status', default='draft',
        tracking=True)

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

    disapproval_reason = fields.Char(string="Reason for Disapproval")
    disapproved_by = fields.Many2one('res.users', string="Disapproved By")
    disapproved_date = fields.Datetime(string="Disapproved Date")

    cancellation_reason = fields.Char(string="Reason for Cancellation")
    cancelled_by = fields.Many2one('res.users', string="Cancelled By")
    cancelled_date = fields.Datetime(string="Cancelled Date")

    initial_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    second_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    third_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    fourth_approver_job_title = fields.Char(compute='get_approver_title', store=True)
    final_approver_job_title = fields.Char(compute='get_approver_title', store=True)

    def approval_dashboard_link(self):
        pass

    def _one2many_field(self):
        return []

    @api.model
    def get_purchase_types(self, include_receipts=False):
        return ['in_invoice', 'in_refund'] + (include_receipts and ['in_receipt'] or [])

    @api.depends('journal_id')
    def _compute_company_id(self):
        for move in self:
            move.company_id = move.journal_id.company_id or move.company_id or self.env.company

    @api.model
    def get_sale_types(self, include_receipts=False):
        return ['out_invoice', 'out_refund'] + (include_receipts and ['out_receipt'] or [])

    def is_sale_document(self, include_receipts=False):
        return self.type in self.get_sale_types(include_receipts)

    def user_error_notif(self, msg):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Error {}'.format(msg)),
                'message': f'{msg}',
                'sticky': True,
            }
        }
        return notification

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
