# # -*- coding: utf-8 -*-
# from odoo import http
# import json
# from odoo.http import Response
# from odoo.http import request


# class ModRequest(http.Controller):

#     @http.route('/api/request_allalll', auth='public', website = False, csrf=False, type='json')
#     def api_request_alls(self, **kw):
#         contact_list = {
#             "name":"Breithner"
#         }
#         return contact_list
        # response = {
        #     'message': '¡Hola desde el controlador de Odoo!',
        #     # 'data': kw
        # }
        # return json.dumps(response)

    # @http.route('/mod_request/mod_request', auth='public', type='json', methods=['GET'], csrf=False)
    # @http.route('/api/requesta', auth='public', type='json')
    # def my_method(self, **kw):
    #     headers = {
    #             'Content-Type': 'application/json',
    #         }
        
        # values = {"orderId":1,"orderValue":99.90,"productId":1,"quantity":1}
        # Aquí puedes agregar tu lógica de negocio y procesamiento de datos
        # return values
        
        # # Ejemplo de respuesta JSON
        # response = {
        #     'message': '¡Hola desde el controlador de Odoo!',
        #     # 'data': kw  # Datos recibidos en la solicitud POST
        # }
        
        # return json.dumps(response,headers =headers)
        # return Response(json.dumps(response), headers=headers)

    # @http.route("/mod_request/mod_request", type="json")
    # def vault_publicw(self, user_id):
    #     """ Get the public key of a specific user """
    #     user = request.env["res.users"].sudo().browse(user_id).exists()
    #     if not user or not user.keys:
    #         return {}

    #     return {"public_key": user.active_key.public}
    # @http.route('/mod_request/mod_request', auth='none', type='json')
    # def index(self, **kwargs):
    #     Response.status = '400'
    #     return {'test':True}
        # return "Hello, world"

#     @http.route('/mod_request/mod_request/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mod_request.listing', {
#             'root': '/mod_request/mod_request',
#             'objects': http.request.env['mod_request.mod_request'].search([]),
#         })

#     @http.route('/mod_request/mod_request/objects/<model("mod_request.mod_request"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mod_request.object', {
#             'object': obj
#         })
