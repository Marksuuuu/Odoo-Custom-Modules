from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    tpc_dm_cm_connection = fields.Many2one('tpc.dm.cm.request', string='Tpc Dm Cm Connection')
    file_links = fields.Text(string='File Links')
    po_reference = fields.Char(string='PO Reference')

    tpc_dm_cm_request_line = fields.One2many('account.move.line.dm.cm', 'account_move_line_for_dm_cm')

    is_processed = fields.Boolean(string='Is Processed')

class AccountMoveLineDmCm(models.Model):
    _name = "account.move.line.dm.cm"
    _description = "Account move line cm cm"


    account_move_line_for_dm_cm = fields.Many2one('account.move')
    ir_attachment_id = fields.Many2one('ir.attachment', string='Related attachment', required=True)
    links = fields.Char(string='Link')




