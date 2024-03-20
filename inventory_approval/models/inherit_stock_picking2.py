from odoo import fields, models, api


class InheritStockPicking2(models.Model):
    _inherit = 'stock.picking'
    _description = 'Inherit Stock Picking'

    check_if_wiv = fields.Boolean(compute='_compute_check_if_wiv', string='Check if Wiv', default=False)

    @api.depends('picking_type_id', 'check_if_wiv')
    def _compute_check_if_wiv(self):
        for rec in self:
            if rec.picking_type_id.name == "WIV Request":
                print(rec.check_if_wiv)
                rec.check_if_wiv = True
                for move_ids in rec.move_line_ids_without_package:
                    move_ids.write({
                        'check_if_shipping_or_transfer': True
                    })
            else:
                print(rec.check_if_wiv)
                rec.check_if_wiv = False
                for move_ids in rec.move_line_ids_without_package:
                    move_ids.write({
                        'check_if_shipping_or_transfer': False
                    })

    @api.depends('product_id')
    def get_eoh(self):
        text = self.product_id.action_update_quantity_on_hand()
        print(text)
        # total_quantity = 0
        # search_for_eoh = self.env['stock.quant'].search([('product_id', '=', self.product_id.id)])
        # for quant_record in search_for_eoh:
        #     location = self.env['stock.location'].search([('id', '=', quant_record.location_id.id)])
        #     if location.name not in ['My Company: Inventory adjustment', 'My Company: Production',
        #                              'Vendors', 'Finished Goods']:
        #         print(quant_record.quantity)
        #         total_quantity += quant_record.quantity
        # print(total_quantity)
