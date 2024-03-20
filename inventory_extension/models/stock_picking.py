from odoo import fields, models, api
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Stock Picking Inventory Extension'

    # name = fields.Char()

    is_shipping_bool = fields.Boolean(string='Is Shipping', default=False, store=True)

    new_sales_order = fields.Many2many('sale.order', string='Sales Order')

    client_order_ref = fields.Char(related='sale_id.client_order_ref', string='Customer Reference')

    source_document2 = fields.Many2one('purchase.order', string='Purchase Order')

    get_connection_field = fields.Many2one('purchase.order', compute='_compute_get_connection', string='Connection', store=False)



    @api.depends('get_connection_field', 'origin', 'user_id')
    def _compute_get_connection(self):
        po = self.env['purchase.order'].search([('name', '=', self.origin)])
        print(po.user_id.id)
        self.get_connection_field = po
        self.user_id = po.user_id.id




    def trigger_stock_move_line_function(self):
        stock_move_line_function = self.env['stock.move.line']
        stock_move_line_function.get_qty_done()

    @api.onchange('picking_type_id')
    def _onchange_is_shipping(self):
        for rec in self:
            if rec.picking_type_id.name == "Shipping":
                rec.is_shipping_bool = True
            else:
                rec.is_shipping_bool = False

    def get_source_origin(self):
        pass

    def get_po(self):
        for record in self:
            print(record.sale_id.client_order_ref   )
            # record.sale_name = record.sale_id.name


    def get_data_move_ids(self):
        move_records = []

        for rec in self.move_line_ids_without_package:
            so_ids = self.env['sale.order'].search([('name', '=', rec.sales_order)])
            if so_ids:
                for so in so_ids:
                    move_records.append({
                        'manufacturing_order_id': rec.manufacturing_order.id,
                        'product_id': rec.product_id.id,
                        'sales_order': rec.sales_order,
                        'sale_id': so.id,  # Use so.id instead of so_ids.id
                        'qty_done': rec.qty_done,
                        'lot_id': rec.lot_id.id,
                        'uom_id': rec.product_uom_id.id,
                        'location_dest_id': rec.location_dest_id.id
                    })
            else:
                # Handle the case when no sale order is found
                move_records.append({
                    'manufacturing_order_id': rec.manufacturing_order.id,
                    'sales_order': rec.sales_order,
                    'product_id': rec.product_id.id,
                    'sale_id': False,  # or any default value
                    'qty_done': rec.qty_done,
                    'lot_id': rec.lot_id.id,
                    'uom_id': rec.product_uom_id.id,
                    'location_dest_id': rec.location_dest_id.id
                })

        self.call_move_ids_function(move_records)

    def call_move_ids_function(self, move_records):
        try:
            picking_type_id = self.env['stock.picking.type'].search([('name', 'ilike', 'Shipping')], limit=1)

            if picking_type_id:
                records = {
                    'partner_id': self.partner_id.id,
                    'location_id': self.location_id.id,
                    'picking_type_id': picking_type_id.id,
                    'scheduled_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                }

                picking_id = self.env['stock.picking'].create(records)

                if picking_id:
                    for record in move_records:
                        one2many_vals = {
                            'product_id': record['product_id'],
                            'picking_id': picking_id.id,
                            'product_uom_id': record['uom_id'],
                            'manufacturing_order': record['manufacturing_order_id'],
                            'sales_order': record['sales_order'],
                            'location_id': self.location_id.id,  # You may adjust this if needed
                            'lot_id': record['lot_id'],
                            'location_dest_id': record['location_dest_id'],
                        }
                        self.env['stock.move.line'].create(one2many_vals)

                    return {'type': 'ir.actions.act_window_close'}
                else:
                    print('Failed to create picking')
                    return {'type': 'ir.actions.act_window_close', 'error': 'Failed to create picking'}
            else:
                print('No "Shipping" picking type found')
        except Exception as e:
            print(f"An error occurred: {e}")
