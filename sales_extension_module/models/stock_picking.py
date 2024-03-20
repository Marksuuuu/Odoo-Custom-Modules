from odoo import fields, models, api
import json
from collections import Counter


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Inherited Stock Picking'

    date_code = fields.Char(string='Date Code')
    flt_vessel = fields.Char(string='Flt/Vessel')

    # origin = fields.Many2many('sale.order', string='Sale Order')

    is_transfer_voucher = fields.Boolean(string='Is Transfer Voucher', readonly=True,
                                         compute='_check_if_is_transfer_voucher', store=False)

    is_shipping = fields.Boolean(string='Is Shipping', readonly=True,
                                         compute='_check_if_shipping', store=False)

    @api.depends('flt_vessel', 'carrier_id', 'carrier_tracking_ref', 'weight', 'shipping_weight')
    def _check_if_is_transfer_voucher(self):
        for rec in self:
            if rec.picking_type_id.name == "Manufacturing - Transfer Voucher":
                rec.is_transfer_voucher = True
            else:
                rec.is_transfer_voucher = False

    @api.depends('picking_type_id', 'is_shipping')
    def _check_if_shipping(self):
        for rec in self:
            if rec.picking_type_id.name == "Shipping":
                print(rec.picking_type_id.name)
                print('True')
                rec.is_shipping = True
            else:
                print(rec.picking_type_id.name)
                print('True')
                rec.is_shipping = False


    def check_so(self):
        records = self.origin
        for record in records:
            so = self.env['mrp.production'].search([('origin', '=', record.name)])
            print(so)


    def get_company(self):
        check_if_not_none = self.env.company
        if check_if_not_none:
            company = self.env.company
        else:
            company = ""
        return company

    def get_customer_ref(self):
        so = self.env['sale.order'].search([('name', '=', self.origin)])
        if so:
            customer_ref = so.client_order_ref
        else:
            customer_ref = ""
        return customer_ref

    #
    # def get_customer_ref(self):
    #     so = self.env['stock.picking'].search([('name', '=', self.origin)])
    #     if so:
    #         customer_ref = so.client_order_ref
    #     else:
    #         customer_ref = ""
    #     return customer_ref



    # def get_delivery_address(self):
    #     print('test')
    #     so = self.env['res.partner'].search([('parent_id', '=', self.partner_id.id)])
    #     print(so)
    # for rec in self:
    #     so = self.env['sale.order'].search([('parent_id', '=', rec.partner_id.id), ('type', '=', 'delivery')])
    #     if so:
    #         customer_ref = so.client_order_ref
    #     else:
    #         customer_ref = ""
    # return customer_ref

    def get_origin_so(self):
        return self.env['stock.picking'].search([('origin', '=', self.origin)])

    def compute_total_qty_to_ship(self):
        total_qty = 0
        for rec in self.move_line_ids_without_package:
            total_qty += rec.product_uom_qty
        print(total_qty)

    def search_so(self):
        so = self.env['sale.order'].search([('name', '=', self.origin)])
        if so:
            mo_result = so.client_order_ref
        return mo_result

    def search_so_address(self):
        so = self.env['sale.order'].search([('name', '=', self.origin)])
        if so:
            address_result = so.partner_shipping_id.name
        return address_result

    def check_many2many_field(self):
        records = self.origin
        for record in records:
            return record.name



