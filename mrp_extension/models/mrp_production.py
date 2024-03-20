# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, _


class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    customer_name = fields.Char(string='Customer', compute='get_customer_name', store=True)
    lot_number = fields.Char(string="Lot Number", compute='get_lot_number', store=True)
    po_number = fields.Char(string="PO Number", compute='get_customer_ref', store=True)
    mo_start_date = fields.Datetime(string="Start Date", store=True)
    remarks = fields.Text(string="Special Instructions", store=True)
    top_side_mark_instruction = fields.Text(string="Top/Side Mark Instructions", store=True)

    # device = fields.Char(
    #     'Device', compute='_compute_attribute_values', store=True,
    #     help='Device attribute value associated with the product variant')
    #
    # bd_number = fields.Char(
    #     'BD Number', compute='_compute_attribute_values', readonly=True, store=True,
    #     help='BD Number attribute value associated with the product variant')

    def get_mo(self):
        return self.env['mrp.production'].search([('origin', '=', self.origin)])

    def get_operation_details(self):
        operation_ids = self.mapped('routing_id.operation_ids')
        operation_names = [operation.name.operation_name for operation in operation_ids.filtered(lambda o: o.cb_print)]
        spec_nos = [operation.spec_no.name for operation in operation_ids.filtered(lambda o: o.cb_print)]
        return list(zip(operation_names, spec_nos))

    # def get_operation_names(self):
    #     operation_ids = self.mapped('routing_id.operation_ids')
    #     return [operation.name.operation_name for operation in operation_ids.filtered(lambda o: o.cb_print)]
    #

    @api.depends('product_id.product_template_attribute_value_ids')
    def get_prod_attr_id(self):
        for rec in self:
            attribute_values = rec.product_id.product_template_attribute_value_ids
            variants_list = []
            for attribute_value in attribute_values:
                attribute_name = attribute_value.attribute_id.name
                attribute_value_name = attribute_value.name
                variants = {
                    'attr_value_name': attribute_value_name,
                    'attr_name': attribute_name
                }
                variants_list.append(variants)
            return variants_list

    @api.depends('origin')
    def get_customer_name(self):
        for rec in self:
            sale_order = self.env['sale.order'].search([('name', '=', rec.origin)], limit=1)

            if sale_order:
                rec.customer_name = sale_order.partner_id.name
                com_date = sale_order.commitment_date

                # print(com_date))
                # print(rec.customer_name)

    @api.depends('origin')
    def get_lot_number(self):
        for rec in self:
            sale_order = self.env['sale.order'].search([('name', '=', rec.origin)], limit=1)
            if sale_order:
                rec.lot_number = sale_order.lot_number

    @api.depends('origin')
    def get_customer_ref(self):
        for rec in self:
            sale_order = self.env['sale.order'].search([('name', '=', rec.origin)], limit=1)
            if sale_order:
                rec.po_number = sale_order.client_order_ref

    def get_shipping_address(self):
        for rec in self:
            sale_order = self.env['sale.order'].search([('name', '=', rec.origin)], limit=1)

            if sale_order:
                name = sale_order.partner_shipping_id.name
                street = sale_order.partner_shipping_id.street
                street2 = sale_order.partner_shipping_id.street2
                city = sale_order.partner_shipping_id.city
                state = sale_order.partner_shipping_id.state_id.name
                zip_code = sale_order.partner_shipping_id.zip
                country = sale_order.partner_shipping_id.country_id.name

                return [name, street, street2, city, state, zip_code, country]
            else:
                return ['', '', '', '', '', '', '']
