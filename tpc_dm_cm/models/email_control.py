from odoo import fields, models, api
from odoo.exceptions import ValidationError


class EmailControl(models.Model):
    _name = 'email.control'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Team Pacific Corporation DM CM'

    name = fields.Many2one('res.users', string='Employee')
    email = fields.Char(related='name.login', string='Email', readonly=True)
    group = fields.Many2one('account.analytic.account', string='Group')
    status = fields.Selection([('active', 'ACTIVE'), ('inactive', 'INACTIVE')], string='Status')
    cc = fields.Boolean(string='CC')
    bcc = fields.Boolean(string='BCC')


class SourceTradeNonTrade(models.Model):
    _name = 'source.trade.non.trade'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Team Pacific Corporation DM CM'
    _rec_name = 'source_trade_n_trade'

    source_ar_lines = fields.One2many('source.trade.non.trade.line', 'ar_conn')
    source_sales_lines = fields.One2many('source.sales.line', 'sales_conn')
    source_trade_n_trade = fields.Char(string='Trade or Non Trade', required=True)

    @api.constrains('source_trade_n_trade')
    def _check_allowed_values(self):
        allowed_values = ['Trade', 'Non-Trade', 'Non-Trade B']
        for record in self:
            if record.source_trade_n_trade and record.source_trade_n_trade not in allowed_values:
                raise ValidationError('Invalid value for Your Text Field. Allowed values are trade or non-trade.')

    @api.constrains('source_trade_n_trade')
    def _check_unique_values(self):
        trade_count = self.search_count([('source_trade_n_trade', '=', 'Trade')])
        non_trade_count = self.search_count([('source_trade_n_trade', '=', 'Non-Trade')])
        non_trade_b_count = self.search_count([('source_trade_n_trade', '=', 'Non-Trade B')])

        if trade_count > 1 or non_trade_count > 1 or non_trade_b_count > 1:
            raise ValidationError('Only one record allowed for Trade and one record allowed for Trade, Non-Trade B, Non-Trade.')


class SourceTradeNonTradeLine(models.Model):
    _name = 'source.trade.non.trade.line'
    _description = 'Team Pacific Corporation DM CM'

    ar_conn = fields.Many2one('source.trade.non.trade')
    name = fields.Many2one('res.users', string='Employee')
    email = fields.Char(related='name.login', string='Email', readonly=True)


class SourceSalesLine(models.Model):
    _name = 'source.sales.line'
    _description = 'Team Pacific Corporation DM CM'

    sales_conn = fields.Many2one('source.trade.non.trade')
    name = fields.Many2one('res.users', string='Employee')
    email = fields.Char(related='name.login', string='Email', readonly=True)
