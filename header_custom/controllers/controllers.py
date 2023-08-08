# -*- coding: utf-8 -*-
# from odoo import http


# class HeaderCustom(http.Controller):
#     @http.route('/header_custom/header_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/header_custom/header_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('header_custom.listing', {
#             'root': '/header_custom/header_custom',
#             'objects': http.request.env['header_custom.header_custom'].search([]),
#         })

#     @http.route('/header_custom/header_custom/objects/<model("header_custom.header_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('header_custom.object', {
#             'object': obj
#         })
