from odoo import fields, models, api
from datetime import datetime


class PriorityList(models.Model):
    _name = 'priority.list'
    _description = 'Priority List'

    name = fields.Char()


    @api.model
    def priority_list_query(self):
        ret_list = []
        req = (
            """
    SELECT
        a.sale_order,
        SPLIT_PART(pc.name, ' - ', 1) AS sbu,
        a.CUSTOMER,
        SPLIT_PART(pc.name, ' - ', 2) AS pkg,
        a.DEVICES,
        a.description,
        a.WIP_ENTITY_NAME,
        a.START_QUANTITY,
        a.RUNNING_QUANTITY,
        a.STATUS,
        a.START_DATE,
        a.ORIG_SOD
    FROM(
        SELECT 
        a.sale_order,
        pt.categ_id,
        a.CUSTOMER,
        pt.name AS DEVICES,
        pt.description,
        a.WIP_ENTITY_NAME,
        a.START_QUANTITY,
        a.RUNNING_QUANTITY,
        a.state,
        a.START_DATE,
        a.ORIG_SOD,
        a.operation_name as STATUS
        FROM (
            SELECT
                a.sale_order,
                a.CUSTOMER,
                pp.product_tmpl_id AS DEVICES,
                a.WIP_ENTITY_NAME,
                a.START_QUANTITY,
                a.RUNNING_QUANTITY,
                a.state,
                a.START_DATE,
                a.ORIG_SOD,
                a.operation_name
            FROM (
                SELECT
                    a.sale_order,
                    rp.name AS CUSTOMER,
                    a.DEVICES,
                    a.WIP_ENTITY_NAME,
                    a.START_QUANTITY,
                    a.RUNNING_QUANTITY,
                    a.state,
                    a.START_DATE,
                    a.ORIG_SOD,
                    a.operation_name
                FROM (
                    SELECT
                        a.sale_order,
                        a.partner_id,
                        a.WIP_ENTITY_NAME,
                        a.START_QUANTITY,
                        a.RUNNING_QUANTITY,
                        sol.product_id AS DEVICES,
                        a.state,
                        a.START_DATE,
                        a.ORIG_SOD,
                        a.operation_name
                    FROM (
                        SELECT
                            so.partner_id,
                            so.name AS sale_order,
                            so.id,
                            a.name AS WIP_ENTITY_NAME,
                            a.product_qty AS START_QUANTITY,
                            a.qty_produced AS RUNNING_QUANTITY,
                            a.state,
                            a.START_DATE,
                            a.ORIG_SOD,
                            a.operation_name
                        FROM (
                            SELECT
                                mp.origin,
                                mp.name,
                                mp.product_qty,
                                mw.qty_produced,
                                mw.state,
                                TO_CHAR(mp.date_deadline, 'DD-Mon-YY') as START_DATE,
                                CONCAT(TO_CHAR(mp.date_deadline, 'DD-Mon-YY') , ' ' , TO_CHAR(mp.date_planned_finished, 'DD-Mon-YY')) as ORIG_SOD,
                                mw.operation_name
                            FROM
                                public.mrp_production mp,
                                public.mrp_workorder mw
                            WHERE
                                mp.id = mw.production_id
                            ORDER BY
                                name DESC
                        ) AS a,
                        public.sale_order AS so
                        WHERE
                            so.name = a.origin
                    ) AS a,
                    public.sale_order_line AS sol
                    WHERE 
                        sol.order_id = a.id
                ) AS a,
                public.res_partner AS rp
                WHERE
                    a.partner_id = rp.id
            ) AS a,
            public.product_product AS pp
            WHERE 
                a.DEVICES = pp.id
        ) AS a,
        public.product_template AS pt
        WHERE 
            a.DEVICES = pt.id 
        )as a,
        public.product_category as pc
        WHERE a.categ_id = pc.id
        """)
        self.env.cr.execute(req)
        for rec in self.env.cr.dictfetchall():
            ret_list.append(rec)
        return ret_list

    def test(self):
        date_string = '01/09/2024 11:50:00'
        date_format = '%m/%d/%Y %H:%M:%S'
        search_date = datetime.strptime(date_string, date_format).date()

        # Set search_hour, search_minute, and search_second to the current time values
        now = datetime.now()
        search_hour = now.hour
        search_minute = now.minute

        # Assuming date_order is a datetime field, searching within a date range
        start_date = datetime.combine(search_date, datetime.min.time())
        end_date = datetime.combine(search_date, datetime.max.time())

        so = self.env['sale.order'].search([
            ('date_order', '>=', start_date),
            ('date_order', '<=', end_date),
        ])
        self.get_sale_order(so)
        for rec in so:

            if rec.date_order:
                order_hour = rec.date_order.hour
                order_minute = rec.date_order.minute
                print(f"{order_hour}:{order_minute:02d}")

                # if (
                #         order_hour == search_hour
                #         and order_minute == search_minute
                # ):
                if rec.order_line:
                    for order_line in rec.order_line:
                        for product in order_line:
                            print(product.product_id.name)

        # Optionally, you can print the current time for reference
        current_time = now.strftime('%H:%M:%S')
        print(f"Current time: {current_time}")

    def get_sale_order(self, so):
        for rec in so:
            print(rec.name)
