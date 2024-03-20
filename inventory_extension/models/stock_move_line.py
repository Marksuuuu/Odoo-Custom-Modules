from odoo import fields, models, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    _description = 'Inherit Stock Move Line'

    # "In the 'Domain' field, make sure to enter the value above the domain field being compared, like this: 'picking_id_compute'."
    manufacturing_order = fields.Many2one('mrp.production', string='Manufacturing Order')
    sales_order = fields.Many2one('sale.order', string='Sales Order', store=True)
    quantity_to_invoice = fields.Integer(string='Quantity to Invoice')
    purchase_order = fields.Char(string='Purchase Order')
    client_order_ref = fields.Char(string='Client Order Ref', store=True)
    mrp_qty_done = fields.Char(string='Quantity Done')
    date_code = fields.Char(related='manufacturing_order.date_code', string='Date Code')

    check_if_shipping_or_transfer = fields.Boolean()

    expiry_date = fields.Datetime(string='Expiry Date')
    received_date = fields.Datetime(string='Received Date')

    # inventory_attachments = fields.Many2many('ir.attachment', string='Attachments')


    @api.depends('mrp_qty_done')
    def get_qty_done(self):
        for rec in self:
            if rec.picking_id and rec.picking_id.origin:
                mrp_production = self.env['mrp.production'].search(
                    [('origin', '=', rec.picking_id.origin.replace(" ", ""))], limit=1)
                if mrp_production:
                    stock_move_line = self.env['stock.move.line'].search([('production_id', '=', mrp_production.id)])
                    print(stock_move_line.qty_done)

    @api.onchange('manufacturing_order')
    def _onchange_manufacturing_order(self):
        sale_order_dict = {}
        lot_dict = {}

        for rec in self.manufacturing_order:
            selected_product = rec.product_id
            selected_sales_order = rec.origin

            if selected_sales_order not in sale_order_dict:
                sale_order = self.env['sale.order'].search([('name', '=', selected_sales_order)], limit=1)
                print(sale_order)
                sale_order_dict[selected_sales_order] = sale_order

            if selected_product.id not in lot_dict:
                lot = self.env['stock.production.lot'].search([('product_id', '=', selected_product.id)], limit=1)
                lot_dict[selected_product.id] = lot

            qty_done = 0
            if rec.state in ['to_close', 'done']:
                qty_done = sum(finished.qty_done for finished in rec.finished_move_line_ids)

            self.product_id = selected_product.id
            self.lot_id = lot_dict[selected_product.id].id

            self.write({
                'sales_order': sale_order.id,
                'client_order_ref': sale_order_dict[selected_sales_order].client_order_ref,
                'mrp_qty_done': qty_done,
                'qty_done': qty_done
            })

    @api.onchange('sales_order')
    def _onchange_sales_order(self):
        for rec in self.sales_order:
            selected_sales_order = rec.name

            if selected_sales_order:
                mos = self.env['mrp.production'].search(
                    [('origin', '=', selected_sales_order), ('state', 'in', ['to_close', 'done'])])

                qty_done = sum(finished.qty_done for mo in mos for finished in mo.finished_move_line_ids)
                print(qty_done)

                if mos:
                    selected_product = mos[0].product_id
                    lot = self.env['stock.production.lot'].search([('product_id', '=', selected_product.id)], limit=1)

                    self.product_id = selected_product.id
                    self.lot_id = lot.id

                    self.write({
                        'client_order_ref': rec.client_order_ref,
                        'mrp_qty_done': qty_done,
                        'qty_done': qty_done
                    })

    # if selected_product.id not in lot_dict:
    #     lot = self.env['stock.production.lot'].search([('product_id', '=', selected_product.id)], limit=1)
    #     lot_dict[selected_product.id] = lot
    #
    # qty_done = 0
    # if rec.state in ['to_close', 'done']:
    #     qty_done = sum(finished.qty_done for finished in rec.finished_move_line_ids)
    #
    # self.product_id = selected_product.id
    # self.lot_id = lot_dict[selected_product.id].id
    #
    # self.write({
    #     'client_order_ref': sale_order_dict[selected_sales_order].client_order_ref,
    #     'mrp_qty_done': qty_done,
    #     'qty_done': qty_done
    # })
