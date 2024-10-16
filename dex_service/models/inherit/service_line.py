from odoo import models, api, fields
from collections import Counter
from datetime import datetime, timedelta
import logging
from odoo.exceptions import UserError
from odoo import models, api
from odoo.http import request
from collections import defaultdict

_logger = logging.getLogger(__name__)


class ServiceLine(models.Model):
    _inherit = 'service.line'

    def get_service_lines_def(self, selected_status=None):
        domain = []
        if selected_status:
            domain.append(('status', '=', selected_status))
        records = self.search_read(domain, ['name', 'status', 'client_name', 'actual_duration'])
        return records

    @api.model
    def get_data_for_all_statuses(self):
        _logger.info('Fetching data for all statuses')

        statuses = ['open', 'cancelled', 'close', 'pending', 'waiting']

        labels = []
        data = []
        colors = [
            '#6495ED', '#DE3163', '#FFBF00', '#CCCCFF', '#6495ED', '#FF00FF',
        ]

        hover_colors = [color + '80' for color in colors]

        for status in statuses:
            records = self.search([('status', '=', status)])
            labels.append(status)
            data.append(len(records))

        return {
            'labels': labels,
            'data': data,
            'colors': colors,
            'hoverColors': hover_colors
        }


    def get_client_data(self, time_frame='day'):
        # Dictionary to store client counts based on the selected time frame
        client_count_by_timeframe = defaultdict(int)

        # Search for all service lines
        services = self.search([])  # Fetch all service lines

        for service in services:
            # Determine the key based on the time frame
            if time_frame == 'day':
                key = service.create_date.strftime('%Y-%m-%d')
            elif time_frame == 'week':
                key = service.create_date.strftime('%Y-%U')  # Year-Week
            elif time_frame == 'month':
                key = service.create_date.strftime('%Y-%m')  # Year-Month
            elif time_frame == 'year':
                key = service.create_date.strftime('%Y')  # Year
            else:
                raise ValueError("Invalid time frame specified.")

            client_count_by_timeframe[key] += 1  # Count per key

        # Prepare data for the chart
        chart_data = {
            'labels': [],
            'data': []
        }

        # Sort keys and prepare the chart data
        for timeframe, count in sorted(client_count_by_timeframe.items()):
            chart_data['labels'].append(timeframe)
            chart_data['data'].append(count)

        return chart_data

    def _get_date_range(self, timeframe):
        today = datetime.now()
        if timeframe == 'daily':
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif timeframe == 'weekly':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(weeks=1)
        elif timeframe == 'monthly':
            start_date = today.replace(day=1)
            end_date = (start_date + timedelta(days=31)).replace(day=1)

        return start_date, end_date
