from odoo import fields, models, api


class TpcDmCmApprovers(models.Model):
    _name = 'tpc.dm.cm.approvers'
    _description = 'Team Pacific Corporation DM CM'

    name = fields.Char()
