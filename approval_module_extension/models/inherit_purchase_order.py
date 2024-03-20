from odoo import fields, models, api
from num2words import num2words
from decimal import Decimal
from fractions import Fraction


class InheritPurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _description = 'Description'


    buyer = fields.Many2one(related='requisition_id.buyer', string='Buyer')

    @api.depends('order_line.price_subtotal')
    def make_total_as_words(self):
        for record in self:
            total_sum = sum(line.price_subtotal for line in record.order_line)

            whole_number, decimal_part = divmod(total_sum, 1)

            rounded_decimal_part = round(decimal_part, 2)

            fraction_part = Fraction(rounded_decimal_part).limit_denominator()

            whole_number_words = num2words(int(whole_number), lang='en').title()
            fraction_words = num2words(fraction_part.numerator, lang='en').title()

            if fraction_part.denominator == 100 and len(str(fraction_part.numerator)) == 1:
                final_words = f"{whole_number_words} and {fraction_part.numerator}/100"
            elif fraction_part.denominator == 100:
                final_words = f"{whole_number_words} and {fraction_words}/{fraction_part.denominator}"
            else:
                final_words = f"{whole_number_words} Only"

            return final_words

    def get_connection_for_stock_picking(self):
        stock_picking_name = self.env['stock.picking'].search([('origin', '=', self.name)])
        for rec in stock_picking_name:
            if rec.picking_type_id.name == 'Warehouse - Receipts':
                return rec

    def get_internal_transfer_for_stock_picking(self):
        stock_picking_name = self.env['stock.picking'].search([('origin', '=', self.name)])
        for rec in stock_picking_name:
            if rec.picking_type_id.name == 'Warehouse - Internal Transfers':
                return rec

    def get_company_registry(self):
        check_if_not_none = self.env.company
        if check_if_not_none:
            registry_number = self.env.company.company_registry
        else:
            registry_number = ""
        return registry_number

    def get_company(self):
        check_if_not_none = self.env.company
        if check_if_not_none:
            return self.env.company
        else:
            return False

    def get_payment_terms(self):
        check_if_not_none = self.invoice_payment_term_id
        if check_if_not_none:
            payment_term = self.invoice_payment_term_id.name
        else:
            payment_term = ""
        return payment_term
