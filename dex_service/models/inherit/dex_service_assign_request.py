from odoo import models, fields, api
import base64
import pandas as pd
import logging
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)



class DexServiceAssignRequest(models.Model):
    _inherit = 'dex_service.assign.request'

    @api.model
    def get_data_for_all_technician(self):
        _logger.info('Fetching data for all technicians')

        # Fetch all technicians linked to this record
        all_technician = self.env['dex_service.assign.request'].sudo().search([])

        product_count = {}
        for product in all_technician:
            for technician in product.technician:
                if technician.name in product_count:
                    product_count[technician.name] += 1
                else:
                    product_count[technician.name] = 1

        result_list = []
        for name, count in product_count.items():
            result_list.append({
                'name': name,
                'total': count,
            })

        labels = [item['name'] for item in result_list]
        data = [item['total'] for item in result_list]

        colors = [
            '#6495ED', '#DE3163', '#FFBF00', '#CCCCFF', '#6495ED', '#FF00FF',
        ]
        _logger.info('labellsss {}'.format(labels))
        hover_colors = [color + '80' for color in colors]

        return {
            'labels': labels,
            'data': data,
            'colors': colors,
            'hoverColors': hover_colors
        }
