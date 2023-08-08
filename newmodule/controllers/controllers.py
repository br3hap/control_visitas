# -*- coding: utf-8 -*-
# from odoo import http


# class Newmodule(http.Controller):
#     @http.route('/newmodule/newmodule', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/newmodule/newmodule/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('newmodule.listing', {
#             'root': '/newmodule/newmodule',
#             'objects': http.request.env['newmodule.newmodule'].search([]),
#         })

#     @http.route('/newmodule/newmodule/objects/<model("newmodule.newmodule"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('newmodule.object', {
#             'object': obj
#         })
