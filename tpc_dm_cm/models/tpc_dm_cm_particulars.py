from odoo import models, fields, api, _


class Particulars(models.Model):
    _name = 'tpc.dm.cm.particulars'
    _description = 'Team Pacific Corporation DM CM'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = 'particulars'


    name = fields.Char(string='Serial No.', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    particulars = fields.Char(string='Particulars')
    description = fields.Char(string='Description')

    def test_insert(self):
        try:
            new_record = self.env['account.move'].create({
                'name': '/',
                'ref': 'BRF/20231130#0001',
                'type': 'out_refund',
                'is_debit_note': True
                # Add other fields accordingly
            })
            print(new_record)
            return new_record.id
        except Exception as e:
            print(f"Error creating record: {e}")




    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('particulars.code') or '/'
        return super(Particulars, self).create(vals)
