from odoo import http
from odoo.http import request

class ServiceController(http.Controller):

    @http.route('/main_dashboard', type='http', auth='user', website=True)
    def display_tabs(self, **kwargs):
        records = request.env['service'].search([])
        return request.render('dex_service.template_id', {
            'records': records,
        })
    
    