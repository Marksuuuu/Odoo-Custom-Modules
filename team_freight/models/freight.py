from odoo import fields, models, api
from odoo.exceptions import UserError


class MrpFreight(models.Model):
    _name = 'mrp.freight'
    _description = 'Freight'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Mrp Freight", readonly=True, copy=False, default='New')
    date_entry = fields.Datetime(string='Date')
    input2 = fields.Float()
    remarks = fields.Char(string='Remarks')
    cost_1 = fields.Float(string='Cost #1')
    cost_2 = fields.Float(string='Cost #2')
    delivery_type = fields.Integer(compute='_compute_count')

    delivery_type_1 = fields.Selection([('air', 'AIR'), ('sea', 'SEA')], string='Delivery Type')
    workorder_count = fields.Integer('# Work Orders', compute='_compute_workorder_count')
    freight_connection_one2many = fields.One2many('mrp.freight.line', 'connection', string='Products')
    freight_cost = fields.Float(string='Freight Cost')

    freight_total_calc = fields.Float(string='Freight Total Calculation')
    freight_total = fields.Float(related='freight_connection_one2many.freight_total', string='Freight Total',
                                 store=True)

    def shipment_type(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Shipment',
            'view_mode': 'tree',
            'res_model': 'mrp.freight.line',
            'domain': [('connection', '=', self.id)],
            'context': "{'create': False}"
        }

    def _compute_count(self):
        for record in self:
            record.delivery_type = self.env['mrp.freight.line'].search_count(
                [('connection', '=', self.id)])
            print(record.delivery_type)

    @api.model
    def create(self, vals):
        try:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('mrp.freight') or 'New'
            result = super(MrpFreight, self).create(vals)
            return result
        except Exception as e:
            raise UserError(f"Error during record creation: {e}")

    def write(self, vals):
        try:
            result = super(MrpFreight, self).write(vals)
            # Additional validation or checks can be added here
            return result
        except Exception as e:
            raise UserError('Error during write operation: {}'.format(e))


def unlink(self):
        try:
            result = super(MrpFreight, self).unlink()
            # Additional validation or checks can be added here
            return result
        except Exception as e:
            raise UserError('Error during unlink operation: {}'.format(e))


class MrpFreightLine(models.Model):
    _name = 'mrp.freight.line'
    _description = 'Mrp Freight Line'

    name = fields.Char(related='connection.name', string='Freight Name', readonly=True, copy=False, store=True)
    date_entry = fields.Datetime(related='connection.date_entry', string='Date')
    connection = fields.Many2one('mrp.freight')
    # freight_name = fields.Char(related='connection.name', string='Freight Name', store=True)
    cost_1 = fields.Float(string='Cost #1', related='connection.cost_1', store=True)
    cost_2 = fields.Float(string='Cost #2', related='connection.cost_2', store=True)
    stock_no = fields.Many2one('product.template', string='Stock Number')
    quantity = fields.Float()
    shipment_weight = fields.Float(related='stock_no.weight', string='Shipment Weight', readonly=True, store=True)
    shipment_volume = fields.Float(related='stock_no.volume', string='Shipment Volume', readonly=True, store=True)
    delivery_type_1 = fields.Selection(related='connection.delivery_type_1', string='Delivery Type', store=True)
    freight_cost = fields.Float(related='connection.freight_cost', string='Freight Cost', store=True)

    percentage = fields.Float('Percentage', compute='calculation_freight', digits=(2, 4))
    total_percentage = fields.Char('Total Percentage')

    total_cost = fields.Float('Total Cost')
    freight_total = fields.Float('Total Freight Cost')

    def write(self, vals):
        try:
            result = super(MrpFreightLine, self).write(vals)
            # Additional validation or checks can be added here
            return result
        except Exception as e:
            raise UserError('Error during write operation: {}'.format(e))

    def unlink(self):
        try:
            result = super(MrpFreightLine, self).unlink()
            # Additional validation or checks can be added here
            return result
        except Exception as e:
            raise UserError('Error during unlink operation: {}'.format(e))

    def calculation_freight(self):
        count_sample = self.search_count([('connection', '=', self.connection.id)])
        del_type = self.connection.delivery_type_1
        if del_type == 'air':
            if count_sample == 1:
                total_compute = 0
                for rec in self:
                    try:
                        compute_percentage = rec.shipment_weight * rec.quantity
                        rec.total_cost = compute_percentage
                        total_compute = total_compute + compute_percentage
                        self.freight_total = total_compute
                    except Exception as e:
                        raise UserError('Error {}, Please Check Weight or Volume in Products..'.format(e))
                for rec in self:
                    try:
                        compute_percentage_total = (rec.shipment_weight * rec.quantity) / total_compute * 100
                        print(compute_percentage_total)
                        rec.percentage = compute_percentage_total
                        rec.total_percentage = str(rec.percentage) + '%'
                    except Exception as e:
                        raise UserError('Error {}, Please Check Weight or Volume in Products..'.format(e))
            else:
                total_compute = 0
                for rec in self:
                    try:
                        compute_percentage = rec.shipment_weight * rec.quantity
                        rec.total_cost = compute_percentage
                        total_compute = total_compute + compute_percentage
                        self.freight_total = total_compute
                    except Exception as e:
                        raise UserError('Error {}, Please Check Weight or Volume in Products..'.format(e))
                for rec in self:
                    try:
                        compute_percentage_total = (rec.shipment_weight * rec.quantity) / total_compute * 100
                        rec.percentage = compute_percentage_total
                        rec.total_percentage = str(rec.percentage) + '%'
                    except Exception as e:
                        raise UserError('Error {}, Please Check Weight or Volume in Products..'.format(e))
        elif del_type == 'sea':
            if count_sample == 1:
                total_compute = 0
                for rec in self:
                    try:
                        compute_percentage = rec.shipment_volume * rec.quantity
                        rec.total_cost = compute_percentage
                        total_compute = total_compute + compute_percentage
                        self.freight_total = total_compute
                    except Exception as e:
                        raise UserError('Error {}, Please Check Weight or Volume in Products..'.format(e))
                for rec in self:
                    try:
                        compute_percentage_total = (rec.shipment_volume * rec.quantity) / total_compute * 100
                        rec.percentage = compute_percentage_total
                        rec.total_percentage = str(rec.percentage) + '%'
                    except Exception as e:
                        raise UserError('Error {}, Please Check Weight or Volume in Products..'.format(e))
            else:
                total_compute = 0
                for rec in self:
                    try:
                        compute_percentage = rec.shipment_volume * rec.quantity
                        rec.total_cost = compute_percentage
                        total_compute = total_compute + compute_percentage
                        self.freight_total = total_compute
                    except Exception as e:
                        raise UserError('Error {}, Please Check Weight or Volume in Products..'.format(e))
                for rec in self:
                    try:
                        compute_percentage_total = (rec.shipment_volume * rec.quantity) / total_compute * 100
                        rec.percentage = compute_percentage_total
                        rec.total_percentage = str(rec.percentage) + '%'
                    except Exception as e:
                        raise UserError('Error {}, Please Check Weight or Volume in Products..'.format(e))
        else:
            print('Not Found')
