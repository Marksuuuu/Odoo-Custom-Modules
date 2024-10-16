from odoo import models, fields, api
import base64
import pandas as pd
import logging
from odoo.exceptions import UserError
from odoo import models, api
from odoo.http import request

_logger = logging.getLogger(__name__)



class AccountMove(models.Model):
    _inherit = 'account.move'

    def name_get(self):
        if self.env.context.get('for_invoice_select'):
            return [
                (line.id, f'{line.name} -- {line.invoice_prefix}-{line.invoice_number}')
                for line in self
            ]
        return super().name_get()

    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        if self.env.context.get('for_invoice_select'):
            if not args:
                args = []
            account_move = self.env['account.move'].search(args + ['|', '|', ('invoice_prefix', operator, name), ('name', operator, name), ('invoice_number', operator, name)], limit=limit)
            if account_move:
                return models.lazy_name_get(self.browse(account_move.ids))
            else:
                return []
        return super()._name_search(name, args, operator, limit, name_get_uid)

    def get_current_company_value(self):

        cookies_cids = [int(r) for r in request.httprequest.cookies.get('cids').split(",")] \
            if request.httprequest.cookies.get('cids') \
            else [request.env.user.company_id.id]

        for company_id in cookies_cids:
            if company_id not in self.env.user.company_ids.ids:
                cookies_cids.remove(company_id)
        if not cookies_cids:
            cookies_cids = [self.env.company.id]
        if len(cookies_cids) == 1:
            cookies_cids.append(0)
        return cookies_cids

    @api.model
    def get_latebillss(self, *post):
        company_id = self.get_current_company_value()

        partners = self.env['res.partner'].search([('active', '=', True)])

        states_arg = ""
        if post[0] != 'posted':
            states_arg = """ account_move.state in ('posted', 'draft')"""
        else:
            states_arg = """ account_move.state = 'posted'"""

        if post[1] == 'this_month':
            self._cr.execute(('''
                                select to_char(account_move.date, 'Month') as month, res_partner.name as bill_partner, account_move.partner_id as parent,
                                sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
                                AND account_move.type = 'in_invoice'
                                AND invoice_payment_state = 'not_paid'
                                AND %s
                                AND Extract(month FROM account_move.invoice_date_due) = Extract(month FROM DATE(NOW()))
                                AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
                                AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                AND account_move.partner_id = res_partner.commercial_partner_id
                                group by parent, bill_partner, month
                                order by amount desc ''') % (states_arg))
        else:
            self._cr.execute((''' select res_partner.name as bill_partner, account_move.partner_id as parent,
                                            sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
                                            AND account_move.type = 'in_invoice'
                                            AND invoice_payment_state = 'not_paid'
                                            AND %s
                                            AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
                                            AND account_move.partner_id = res_partner.commercial_partner_id
                                            AND account_move.company_id in ''' + str(tuple(company_id)) + '''
                                            group by parent, bill_partner
                                            order by amount desc ''') % (states_arg))

        result = self._cr.dictfetchall()
        bill_partner = [item['bill_partner'] for item in result]

        bill_amount = [item['amount'] for item in result]

        amounts = sum(bill_amount[9:])
        name = bill_partner[9:]
        results = []
        pre_partner = []

        bill_amount = bill_amount[:9]
        bill_amount.append(amounts)
        bill_partner = bill_partner[:9]
        bill_partner.append("Others")
        records = {
            'bill_partner': bill_partner,
            'bill_amount': bill_amount,
            'result': results,

        }
        return records