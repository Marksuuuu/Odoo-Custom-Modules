from odoo import fields, models, api


class AccountMoveAttachments(models.Model):
    _name = 'account.move.attachments'
    _description = 'Description'

    tpc_dm_cm_request_ids = fields.Many2one('tpc.dm.cm.request', string="Tpc DM CM")
    attachments_ids = fields.Many2one('ir.attachment', string='Attachments')
    file_links = fields.Char(string='File Links')

