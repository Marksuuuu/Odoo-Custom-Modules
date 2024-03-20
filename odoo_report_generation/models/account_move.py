from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Inherited Account Move'

    hawb = fields.Char(string='HawB No.')
    forwarder = fields.Char(string='Forwarder')
    total_cartons = fields.Integer(string='Total Cartons')

    def print_template(self):
        for rec in self:
            # Extract customer IDs from the record
            customer_ids = [customer.id for customer in rec.partner_id]

            # Define the domain to search for records with matching customer IDs
            domain = [('customers', 'in', customer_ids)]

            # Perform the search using the domain
            records = self.env['report.template.setup'].search(domain)

            # Iterate over each record in records
            for record in records:
                # Iterate over each customer in the record's customers
                for customer in record.customers:
                    # Check if the customer's partner_id matches any of the customer_ids
                    if customer.id in customer_ids:
                        # Get the report model using the technical name
                        report_model = self.env['ir.actions.report']._get_report_from_name(record.associated_reports.report_name)
                        print(report_model)
                        print(record.associated_reports.report_name)

                        # Check if the report model exists
                        if report_model:
                            # Call report_action method to print the report
                            return report_model.report_action(self)
                        else:
                            # Handle the case when the report model doesn't exist
                            print("Report model not found for:", record.associated_reports.report_name)

    def get_qty_done_from_mo(self):
        if isinstance(self.invoice_origin, list):
            for origin in self.invoice_origin:
                print(origin.replace(" ", ""))
        elif isinstance(self.invoice_origin, str):
            origins = [rec.strip() for rec in self.invoice_origin.split(',')]
            mrp_productions = self.env['mrp.production'].search([('origin', 'in', origins)])
            result_list = []

            for mrp in mrp_productions:
                if mrp.state in ['done', 'to_close']:
                    result_list.append(mrp)
                else:
                    result_list.append((mrp, None))

            # Filter out tuples with any element being None
            filtered_result_list = [item for item in result_list if all(e is not None for e in item)]

            print(filtered_result_list)
            return filtered_result_list
        else:
            print("Unexpected type for invoice_origin:", type(self.invoice_origin))

    def get_mo_from_mo(self):
        if isinstance(self.invoice_origin, list):
            for origin in self.invoice_origin:
                print(origin.replace(" ", ""))
        elif isinstance(self.invoice_origin, str):
            origins = [rec.strip() for rec in self.invoice_origin.split(',')]
            mrp_productions = self.env['mrp.production'].search([('origin', 'in', origins)])
            for mrp in mrp_productions:
                if mrp.state in ['done', 'to_close']:
                    return mrp
                else:
                    return False
        else:
            print("Unexpected type for invoice_origin:", type(self.invoice_origin))

    def get_total_qty_done(self):
        if isinstance(self.invoice_origin, list):
            for origin in self.invoice_origin:
                print(origin.replace(" ", ""))
        elif isinstance(self.invoice_origin, str):
            origins = [rec.strip() for rec in self.invoice_origin.split(',')]
            mrp_productions = self.env['mrp.production'].search([('origin', 'in', origins)])
            result_list = []
            total_qty_done = 0

            for mrp in mrp_productions:
                if mrp.state in ['done', 'to_close']:
                    total_qty_done += sum(ids.qty_done for ids in mrp.finished_move_line_ids)
                    result_list.append((mrp, sum(ids.qty_done for ids in mrp.finished_move_line_ids)))
                else:
                    result_list.append((mrp, None))

            return total_qty_done
        else:
            print("Unexpected type for invoice_origin:", type(self.invoice_origin))

    def test(self):
        result = None
        count = 0  # Counter to track the number of non-empty values encountered

        for rec in self.line_ids:
            if rec.credit:
                count += 1
                if count == 2:
                    result = rec.credit
                    break  # Exit the loop once the second non-empty credit is found
            elif rec.debit:
                count += 1
                if count == 2:
                    result = rec.debit
                    break  # Exit the loop once the second non-empty debit is found

        return result

    def check_amount_total_signed(self):
        result = None
        for rec in self.line_ids:
            if rec.credit:
                result = rec.credit
                print(result)
                break  # Exit the loop once a non-empty credit is found
            elif rec.debit:
                result = rec.debit
                break  # Exit the loop once a non-empty debit is found

        return result

    def check_forex_values(self, curr):
        currency_val = self.env['res.currency'].search([('name', '=', curr)])

        if not currency_val:
            return None

        forex_rates = currency_val.rate_ids

        if not forex_rates:
            return None

        first_record = forex_rates[0]

        if isinstance(first_record.rate, float):
            return first_record.rate
        else:
            return first_record.rate

    def check_currency(self):
        if self.currency_id.name == 'PHP':
            return self.check_forex_values('PHP')
        elif self.currency_id.name == 'USD':
            return self.check_forex_values('PHP')
        elif self.currency_id.name == 'JPY':
            return self.check_forex_values('JPY')
        elif self.currency_id.name == 'GBP':
            return self.check_forex_values('GBP')
        elif self.currency_id.name == 'EUR':
            return self.check_forex_values('EUR')
        else:
            return ''

    def print_invoice_voucher(self):
        return self.env.ref('sales_extension_module.invoice_voucher').report_action(self)

    def print_payable_voucher_ext(self):
        return self.env.ref('sales_extension_module.test_payable_voucher').report_action(self)

    def print_debit_voucher_normal(self):
        return self.env.ref('sales_extension_module.debit_note_extension').report_action(self)

    def print_credit_voucher_normal(self):
        return self.env.ref('sales_extension_module.credit_note_extension').report_action(self)

    def print_debit_credit_voucher_without_fee(self):
        return self.env.ref('sales_extension_module.debit_note_without_fee_extension').report_action(self)

    def check_for_microchips(self):
        if not self.partner_id:
            return False  # Or handle the case when there are no partners

        for partner in self.partner_id:
            if not partner.name or not isinstance(partner.name, str):
                continue  # Skip if the name is not a string or is empty

            words = partner.name.lower().split()
            microchip_found = any("microchip" in word for word in words)
            if microchip_found:
                return True

        return False  # Microchip not found in any partner name

    def get_customer_ref(self):
        so = self.env['sale.order'].search([('name', '=', self.invoice_origin)])
        if so:
            customer_ref = so.client_order_ref
        else:
            customer_ref = ""
        return customer_ref

    def get_company_registry(self):
        check_if_not_none = self.env.company
        if check_if_not_none:
            registry_number = self.env.company.company_registry
        else:
            registry_number = ""
        return registry_number

    def get_company_country(self):
        check_if_not_none = self.env.company
        if check_if_not_none:
            country_id = self.env.company.country_id.name
        else:
            country_id = ""
        return country_id

    def get_partner_id_tax_id(self):
        check_if_not_none = self.partner_id
        if check_if_not_none:
            tax_id = self.partner_id.vat
        else:
            tax_id = ""
        return tax_id

    def get_payment_terms(self):
        check_if_not_none = self.invoice_payment_term_id
        if check_if_not_none:
            payment_term = self.invoice_payment_term_id.name
        else:
            payment_term = ""
        return payment_term

    def get_delivery_courier(self):
        so = self.env['sale.order'].search([('name', '=', self.invoice_origin)])
        sp = self.env['stock.picking'].search([('origin', '=', so.name)], limit=1)
        if sp:
            carrier = sp.carrier_id.name
        else:
            carrier = ""
        return carrier

    def get_tracking_ref(self):
        so = self.env['sale.order'].search([('name', '=', self.invoice_origin)])
        sp = self.env['stock.picking'].search([('origin', '=', so.name)], limit=1)
        if sp:
            tracking_ref = sp.carrier_tracking_ref
        else:
            tracking_ref = ""
        return tracking_ref

    def get_currency(self):
        if self.currency_id:
            currency = self.currency_id
        else:
            currency = ""
        return currency

    def get_mo(self):
        return self.env['mrp.production'].search([('origin', '=', self.invoice_origin)])

    def get_flt_vessel(self):
        so = self.env['sale.order'].search([('name', '=', self.invoice_origin)])
        sp = self.env['stock.picking'].search([('origin', '=', so.name)], limit=1)
        if sp:
            flt_vessel = sp.flt_vessel
        else:
            flt_vessel = ""
        return flt_vessel

    def get_shipping_weight(self):
        so = self.env['sale.order'].search([('name', '=', self.invoice_origin)])
        sp = self.env['stock.picking'].search([('origin', '=', so.name)], limit=1)
        if sp:
            weight = sp.shipping_weight
        else:
            weight = ""
        return weight

    def get_so(self):
        so = self.env['sale.order'].search([('name', '=', self.invoice_origin)])
        if so:
            weight = so.name
        else:
            weight = ""
        return weight

    def get_weight(self):
        so = self.env['sale.order'].search([('name', '=', self.invoice_origin)])
        sp = self.env['stock.picking'].search([('origin', '=', so.name)], limit=1)
        if sp:
            weight = sp.weight
        else:
            weight = ""
        return weight


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _description = 'Inherited Account Move Line'

    child_lot = fields.Char(string='Child Lot')

    ## This is for Customer be careful about this function
    @api.onchange('product_id')
    def product_id_onchange_domain(self):
        for rec in self:
            if rec.product_id and rec._origin:  # Check if product_id exists and record is not being created or deleted
                domain_uom = [('id', '=', rec.uom_id.id)]
                return {'domain': {'product_uom_id': domain_uom}}
            else:
                return {'domain': {'product_uom_id': []}}  # Clear domain filter on product_uom_id
