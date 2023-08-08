# -*- coding: utf-8 -*-
# from odoo import http


# class DeliveryStatusTrace(http.Controller):
#     @http.route('/delivery_status_trace/delivery_status_trace/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/delivery_status_trace/delivery_status_trace/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('delivery_status_trace.listing', {
#             'root': '/delivery_status_trace/delivery_status_trace',
#             'objects': http.request.env['delivery_status_trace.delivery_status_trace'].search([]),
#         })

#     @http.route('/delivery_status_trace/delivery_status_trace/objects/<model("delivery_status_trace.delivery_status_trace"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('delivery_status_trace.object', {
#             'object': obj
#         })
