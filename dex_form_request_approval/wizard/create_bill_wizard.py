from odoo import models, fields, api, _
import base64
import pandas as pd
import logging
from datetime import date
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class CreateBillWizard(models.TransientModel):
    _name = 'create.bill.wizard'

    cbwl_lines = fields.One2many('create.bill.wizard.line', 'cbwl_ids')

    tnvf_ids = fields.Char()

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    # transport_vehicle_type = fields.Many2one('transport.network.vehicle.type', string='Transport Vehicle Type')

    vehicle_type_rate = fields.Float(string='Transport Vehicle Rate')

    total_rate = fields.Float(string="Total", store=True)

    cargo_type = fields.Selection([
        ('personnel', 'Personnel'),
        ('package', 'Package')], default='personnel')

    test = fields.Char()

    requesters_id = fields.Many2one('hr.employee', string='Requesters')

    currency_id = fields.Many2one('res.currency')

    journal_id = fields.Many2one('account.journal', string='Journal')

    invoice_payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms',
                                              domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                              readonly=True, states={'draft': [('readonly', False)]}, tracking=True)

    invoice_date_due = fields.Date(string='Due Date', readonly=True, index=True, copy=False,
                                   states={'draft': [('readonly', False)]}, tracking=True)

    state = fields.Selection(
        selection=[('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'),
                   ('disapprove', 'Disapproved'), ('cancel', 'Cancelled')],
        default='draft', tracking=True)

    partner_id = fields.Many2one('res.partner', domain=[('supplier_rank', '>', 1)])

    def generate_bill(self):
        active_id = self._context.get('active_id')
        active_model = self.env.context.get('active_model')
        requests_res = self.env[active_model].browse(active_id)
        data = {
            'id': requests_res.id,
            'invoice_date_due': self.invoice_date_due,
            'invoice_payment_term_id': self.invoice_payment_term_id.id,
            'invoice_date': date.today(),
            'date': date.today(),
            'partner_id': self.partner_id.id,
            'ref': 'from transport network vehicle {}'.format(requests_res.name),
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_state': 'in_invoice'
        }
        data_from_one2many = self.cbwl_lines
        for_checking = self._checking_if_have_valid_entries(data_from_one2many, requests_res)
        if for_checking:
            new_move_id = self._account_move(data, requests_res)
            self._account_move_line(new_move_id, data_from_one2many, requests_res)
        else:
            raise ValidationError('Invalid Entry.. Missing Field')

    def _account_move(self, data, requests_res):
        new_record = self.env['account.move'].create({
            'invoice_date': data.get('invoice_date'),
            'partner_id': data.get('partner_id'),
            'state': 'draft',
            'date': data.get('date'),
            'invoice_user_id': data.get('invoice_user_id'),
            'ref': data.get('ref'),
            'type': data.get('invoice_state'),
            'transport_network_vehicle_ids': requests_res.id,
            'currency_id': data.get('currency_id'),
            'invoice_payment_term_id': data.get('invoice_payment_term_id'),
            'invoice_date_due': data.get('invoice_date_due'),
        })
        self._account_move_connection(new_record, requests_res)
        return new_record

    def _account_move_connection(self, move_record, requests_res):
        try:
            requests_res.is_bill_created = move_record.id
            pass
        except Exception as e:
            raise ValueError(f"Error connecting account move: {e}")

    def _account_move_line(self, move_record, data, requests_res):
        for record in data:
            move_record.write({'invoice_line_ids': [
                (0, 0, {
                    'quantity': 1,
                    'name': record.label,
                    'price_unit': record.tnvf_amount,
                    'account_id': record.account_id.id,
                    'analytic_account_id': record.analytic_account_id.id,
                })]})

    def _checking_if_have_valid_entries(self, data, requests_res):
        for record in data:
            if not record.analytic_account_id.id or not record.account_id.id:
                return False
        return True


class CreateBillWizardLine(models.TransientModel):
    _name = 'create.bill.wizard.line'

    cbwl_ids = fields.Many2one('create.bill.wizard')
    label = fields.Char()
    def _get_account_domain(self):
        expense_type = self.env.ref('account.data_account_type_expenses')
        return [('user_type_id', '=', expense_type.id),]
    account_id = fields.Many2one('account.account', domain= lambda self: self._get_account_domain())

    tnvf_personnel = fields.Char(string='Personnel')
    tnvf_package = fields.Char(string='Package')
    tnvf_from = fields.Char(string='From')
    tnvf_to = fields.Char(string='To')
    tnvf_amount = fields.Float(string='Rate')
    tnvf_purpose = fields.Char(string='Purpose')

    test = fields.Char()

    # Overload of fields defined in account
    analytic_account_id = fields.Many2one('account.analytic.account', store=True, readonly=False, copy=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', store=True, readonly=False, copy=True)
