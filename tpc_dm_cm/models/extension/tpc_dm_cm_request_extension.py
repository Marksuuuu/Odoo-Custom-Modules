from odoo import fields, models, api


class TpcDmCmRequest(models.Model):
    _inherit = 'tpc.dm.cm.request'

    total_count = fields.Integer()

    # @api.model
    # def _count_records(self):
    #     # Specify your search criteria
    #     domain = [('state', '=', 'approved')]
    #
    #     # Use search_count to count records that match the criteria
    #     record_count = self.env['tpc.dm.cm.request'].search_count(domain)
    #
    #     model = self.env['tpc.dm.cm.request']
    #     model.write({
    #         'total_count': record_count
    #     })


