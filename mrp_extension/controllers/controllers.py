# -*- coding: utf-8 -*-
# from odoo import http


# class MrpExtension(http.Controller):
#     @http.route('/mrp_extension/mrp_extension/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mrp_extension/mrp_extension/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mrp_extension.listing', {
#             'root': '/mrp_extension/mrp_extension',
#             'objects': http.request.env['mrp_extension.mrp_extension'].search([]),
#         })

#     @http.route('/mrp_extension/mrp_extension/objects/<model("mrp_extension.mrp_extension"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mrp_extension.object', {
#             'object': obj
#         })
