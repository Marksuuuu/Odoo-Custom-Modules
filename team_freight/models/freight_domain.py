from odoo import fields, models, api
from odoo.tools import datetime


class FreightDomain(models.Model):
    _name = 'freight.domain'
    _description = 'Freight Domain'

    total = fields.Float()




    def action_compute_mrp(self):
        pass
        # # self.call_here()
        # test1 = self.env['freight.cron.model']
        #
        # self.env.cr.execute("""SELECT (sum(shipment_weight) / sum(shipment_volume)) + (sum(cost_1) + sum(cost_1)) as total FROM mrp_freight""")
        # sample = self.env.cr.dictfetchone()
        # print("sample -->", sample)
        # # for rec in test1:
        # date_comp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # no = sample['total']
        #
        # test1.create({
        #     'total': no,
        #     'date_compute': date_comp
        # })
        #
        # print(no)

        # self.env['mrp.freight'].write({
        #                             'sample': no
        #                              })
        # return super(FreightDomain, self).write(vals)

        #     rec.write({
        #         'sample': no
        #     })
        # print('sampple -->', vals)

        #
        # record = self.env['mrp.freight'].create({
        #     'total': sample
        # })
        # return record

        # self.env.cr.execute("""SELECT count(id) cnt from stock_picking where is_dmr = 1""")
        # count_mrb_dispo = self.env.cr.dictfetchone()
        #
        # code = 'DMR#'
        # no = str(count_mrb_dispo['cnt'] + 1)
        # dmr_no = code + no.zfill(4)
        # self.dmr_no = dmr_no
        # test1 = self.env['mrp.workorder'].search_count([('state', '=', 'progress')])
        # test2 = self.env['mrp.workorder'].mapped(lambda r: r.sample_qty + r.amount)
        # print(test)
        # print(test1)
        # print(test2)
        # test = self.env['mrp.freight']
        # for rec in test:
        #     print(rec)
        # print(test1)
        # print(test)
