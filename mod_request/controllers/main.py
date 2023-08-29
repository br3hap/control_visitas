from odoo import http
from odoo.http import request
import base64
from datetime import datetime   
import pytz

local = pytz.timezone("America/Lima")

formate = "%Y-%m-%d %H:%M:%S"



class Main(http.Controller):

    def name_request_exists(self, name_request):
        name_request_id = request.env['mod.request'].sudo().search(
            [('name', '=', name_request)], limit=1)
        if not name_request_id:
            return False
        return name_request_id
    

    def format_date(self, date_request, formate):
        date = datetime.strptime(date_request, formate)
        local_dt = local.localize(date, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        date_utc = utc_dt.strftime(formate)
        return date_utc

    def name_requests_and_requirement_exists(self, mod_request_id, name_requirement):
        name_request_and_requirement = request.env['mod.request.requirements'].sudo().search(
            [
                ('mod_request_id', '=',
                 mod_request_id), ('name_requirement', '=', name_requirement)
            ])
        if not name_request_and_requirement:
            return False
        return name_request_and_requirement
    

    def file_request_judicial_purchased_exists(self,mod_request_id,file_name):
        name = request.env['mod.request.upload.judicial.purchased'].sudo().search([
            ('mod_request_id','=',mod_request_id),
            ('file_name_purchased','=',file_name)
            ])
        if not name:
            return False
        return name
    

    def file_request_judicial_supported_exists(self,mod_request_id,file_name):
        name = request.env['mod.request.upload.judicial.supported'].sudo().search([
            ('mod_request_id','=',mod_request_id),
            ('file_name_supported','=',file_name)
            ])
        if not name:
            return False
        return name

    def partner_dni_ruc_exists(self, number):
        dni_ruc = request.env['res.partner'].sudo().search(
            [('vat', '=', number)])
        if not dni_ruc:
            return False
        return dni_ruc
    
    def moneda_exists(self, name):
        moneda = request.env['res.currency'].sudo().search([('name','=',name)])
        if not moneda:
            return False
        return moneda
    
    def employee_exists(self, dni):
        number_dni = request.env['hr.employee'].sudo().search([('identification_id','=',dni)])
        if not number_dni:
            return False
        return number_dni


    def formatted_data(self, text):
        texto_sin_llaves = text.replace('{', '').replace('}', '')
        texto_sin_comillas = texto_sin_llaves.replace("'", "")
        texto_final = texto_sin_comillas.replace(", ", "\n")
        return texto_final


    @http.route('/api/requests', auth='public', website=True, type='json', methods=['GET', 'POST'], csrf=False,  cors="*")
    def api_requests(self, **kw):
        if not kw.get('token'):
            return {'status_code': 400, 'response': "Add token"}

        if not kw.get('requests'):
            return {'status_code': 400, 'response': "Add request"}

        rest_api_token = request.env["rest.api.token"]
        token = rest_api_token.sudo().search(
            [('account_token', '=', kw.get('token'))], limit=1)
        data_list = []
        data = {}
        for l in kw.get('requests'):
            data = {
                "name": l['name'],
                "name_applicant": l['name_applicant'],
                "process_request": l['process_request'],
                "format_request": l['format_request'],
                "description": l['description'],
                "seller": l['seller'],
                "type_request": l['type_request'],
                "date_request": l['date_request'],
                "currency_id": l['currency_id'],
                "partner_id": l['partner_ruc_dni'],
                "state": l['state'],
                "amount": l['amount'],
                "bank": l['bank'],
                "account": l['account']
            }
            data_list.append(data)

        if token:

            list_name_request = []
            for primer_name in data_list:
                list_name_request.append(primer_name)
            for ln in list_name_request:
                name_request = self.name_request_exists(ln['name'])
                number_ruc_dni = self.partner_dni_ruc_exists(ln['partner_id'])
                name_moneda = self.moneda_exists(ln['currency_id'])
                employee_dni = self.employee_exists(ln['seller'])

                formatted_utc_dt = self.format_date(ln['date_request'], formate)

                data_update = {
                    "name_applicant": ln['name_applicant'],
                    "process_request": ln['process_request'],
                    "format_request": ln['format_request'],
                    "description": ln['description'],
                    "seller": employee_dni.id if employee_dni else None,
                    "type_request": ln['type_request'],
                    "date_request": formatted_utc_dt,
                    # "date_request": ln['date_request'],
                    "currency_id": name_moneda.id if name_moneda else '',
                    "partner_id": number_ruc_dni.id if number_ruc_dni else '',
                    "state": ln['state'],
                    "amount": ln['amount'],
                    "bank": ln['bank'],
                    "account": ln['account']
                }
                data_create = {
                    'name': ln['name'],
                    "name_applicant": ln['name_applicant'],
                    "process_request": ln['process_request'],
                    "format_request": ln['format_request'],
                    "description": ln['description'],
                    "seller": employee_dni.id if employee_dni else '',
                    "type_request": ln['type_request'],
                    "date_request": formatted_utc_dt,
                    # "date_request": ln['date_request'],
                    "currency_id": name_moneda.id if name_moneda else '',
                    "partner_id": number_ruc_dni.id if number_ruc_dni else '',
                    "state": ln['state'],
                    "amount": ln['amount'],
                    "bank": ln['bank'],
                    "account": ln['account']
                }
                if name_request:
                    name_request.sudo().write(data_update)
                else:
                    http.request.env['mod.request'].sudo().create(data_create)
        else:
            return {'status_code': 400, 'response': "Failed token"}
        return {'status_code': 200, 'response': 'successfully', 'Access-Control-Allow-Origin': '*'}
    

    @http.route('/api/requirement', auth='public', website=True, type='json', methods=['GET', 'POST'], csrf=False, cors="*")
    def api_requirement(self, **kw):
        if not kw.get('token'):
            return {'status_code': 400, 'response': "Add token"}

        if not kw.get('requirements'):
            return {'status_code': 400, 'response': "Add requirements"}

        rest_api_token = request.env["rest.api.token"]
        token = rest_api_token.sudo().search(
            [('account_token', '=', kw.get('token'))], limit=1)
        data_list = []
        data = {}
        for r in kw.get('requirements'):
            data = {
                "mod_request_id": r['cod_request'],
                "name_requirement": r['name_requirement'],
                "case_requirement": r['case_requirement'],
                "proceedings_requirement": r['proceedings_requirement'],
                "amount_requirement": r['amount_requirement'],
                "date_request_requirement": r['date_request_requirement'],
                "court_entity_requirement": r['court_entity_requirement'],
                "ruc_dni_requirement": r['ruc_dni_requirement'],
                "description_requirement": r['description_requirement'],
                "json_text": r['json_text'],
                "partner_id":r['partner_ruc']
            }
            data_list.append(data)
            print("data_list", data_list)
        if token:
            list_name_request = []
            for primer_name in data_list:
                list_name_request.append(primer_name)
            for ln in list_name_request:
                name_request = self.name_request_exists(ln['mod_request_id'])
                name_request_and_requirement = self.name_requests_and_requirement_exists(ln['mod_request_id'], ln['name_requirement'])

                formatted_utc_dt = self.format_date(ln['date_request_requirement'], formate)
                number_ruc_dni = self.partner_dni_ruc_exists(ln['partner_id'])

                # data = {}
                # # data.update(ln['json_text'])
                # print("data", type(dict(ln['json_text'])))
                # formatted_data = ',\n'.join([f"{k}: {v}" for k, v in data.items()])
                # print('ln', formatted_data)
                text_end = self.formatted_data(ln['json_text'])

                data_update = {
                    'mod_request_id': name_request.id,
                    'name_requirement': ln['name_requirement'],
                    'case_requirement': ln['case_requirement'],
                    'proceedings_requirement': ln['proceedings_requirement'],
                    'amount_requirement': ln['amount_requirement'],
                    'date_request_requirement': formatted_utc_dt,
                    # 'date_request_requirement': ln['date_request_requirement'],
                    'court_entity_requirement': ln['court_entity_requirement'],
                    'ruc_dni_requirement': ln['ruc_dni_requirement'],
                    'description_requirement': ln['description_requirement'],
                    'json_text': text_end,
                    # 'json_text': ln['json_text'],
                    # "partner_id":ln['partner_ruc']
                    "partner_id":number_ruc_dni.id if number_ruc_dni else '',
                    # 'tag_sustentado':'pending'

                }
                if name_request_and_requirement:
                    name_request_and_requirement.sudo().write(data_update)
                elif name_request:
                    http.request.env['mod.request.requirements'].sudo().create(
                        data_update)
        else:
            return {'status_code': 400, 'response': "Failed token"}

        return {'status_code': 200, 'response': 'successfully', 'Access-Control-Allow-Origin': '*'}
    

    @http.route('/api/upload_file/administrative', type='http', auth='none', csrf=False, methods=['POST'], cors="*")
    def upload_file_administrative(self, **post):
        # token = request.httprequest.headers.get('token')
        file = request.httprequest.files.get('file')
        cod_request = post.get('cod_request')
        token = post.get('token')
        rest_api_token = request.env["rest.api.token"]
        tok = rest_api_token.sudo().search(
            [('account_token', '=', token)], limit=1)
        if tok:
            name_request = self.name_request_exists(cod_request)
            if name_request:
                file_content = file.read()
                file_base64 = base64.b64encode(file_content)
                name_request.sudo().write({'file_request':file_base64, 'file_name':file.filename})


    @http.route('/api/upload_file/judicial', type='http', auth='none', csrf=False, methods=['POST'], cors="*")
    def upload_file_judicial(self, **post):
        # token = request.httprequest.headers.get('token')
        file = request.httprequest.files.get('file')
        cod_request = post.get('cod_request')
        token = post.get('token')
        rest_api_token = request.env["rest.api.token"]
        tok = rest_api_token.sudo().search(
            [('account_token', '=', token)], limit=1)
        if tok:
            name_request = self.name_request_exists(cod_request)
            if name_request:
                file_content = file.read()
                file_base64 = base64.b64encode(file_content)
                # if name_request.state == 'subscriber':
                #     file_exists = self.file_request_judicial_purchased_exists(name_request.id, file.filename)
                #     if file_exists:
                #         file_exists.sudo().write({
                #             'file_purchased':file_base64,
                #             'file_name_purchased':file.filename
                #         })
                #     else:
                #         http.request.env['mod.request.upload.judicial.purchased'].sudo().create({
                #             'mod_request_id':name_request.id,
                #             'file_purchased':file_base64,
                #             'file_name_purchased':file.filename
                #         })
                if name_request.state == 'subscriber':
                    file_exists = self.file_request_judicial_supported_exists(name_request.id, file.filename)
                    if file_exists:
                        file_exists.sudo().write({
                            'file_supported':file_base64,
                            'file_name_supported':file.filename
                        })
                    else:
                        http.request.env['mod.request.upload.judicial.supported'].sudo().create({
                            'mod_request_id':name_request.id,
                            'file_supported':file_base64,
                            'file_name_supported':file.filename
                        })

                elif name_request.state == 'pending' and name_request.process_request == 'repayment':
                    file_exists = self.file_request_judicial_supported_exists(name_request.id, file.filename)
                    if file_exists:
                        file_exists.sudo().write({
                            'file_supported':file_base64,
                            'file_name_supported':file.filename
                        })
                    else:
                        http.request.env['mod.request.upload.judicial.supported'].sudo().create({
                            'mod_request_id':name_request.id,
                            'file_supported':file_base64,
                            'file_name_supported':file.filename
                        })







    
