# custom_web_view/controllers/controllers.py
from odoo import http
from odoo.http import request

class CustomWebViewController(http.Controller):
    @http.route('/custom_web_view', auth='user', website=True)
    def custom_web_view(self, **kwargs):
        return request.render('priority_list.custom_web_view_template', {})
