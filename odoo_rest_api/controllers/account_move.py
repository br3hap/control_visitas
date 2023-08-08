from email import message
import json
from urllib import response
from odoo import http
from odoo.http import request

class Main(http.Controller):
    
    

    # =========================================CLIENT CREATE =====================

    def customer_exists(self,name_customer):
        partner_id = request.env["customer.rest.api"].sudo().search([('name','=',name_customer)], limit=1)
        if not partner_id:
            return False
        return partner_id


    def client_api_create(self,line,token):
     
        data={}
        response = {'code':200,'detail':'successful','data':''}
        customer_rest_api = request.env["customer.rest.api"]
        type_doc_id = request.env['l10n_latam.identification.type'].search([('l10n_pe_vat_code','=',line.get('tipo_doc'))],limit=1)
        message = ""
        if not type_doc_id:
            message += 'Invalid Document Type'
            response.update({'code':400,'detail': message})

        ubigeo = line.get('ubigeo')
        if ubigeo:
            city = ubigeo[0:4] 
            state = ubigeo[0:2] 
            distric = ubigeo

            district_id = request.env['l10n_pe.res.city.district'].search([('code','=',distric)], limit=1)
            city_id = request.env['res.city'].search([('l10n_pe_code','=',city)], limit=1)
            state_id = request.env['res.country.state'].search([('code','=',state),('country_id','=',city_id.country_id.id)], limit=1)
  
            if  state_id  :
                data["state_id"] = state_id.id
            if  city_id:
                data["city_id"] = city_id.id 
                data["country_id"] =  city_id.country_id.id
            if  district_id:
                data["l10n_pe_district"] = district_id.id
        
        
        
        # === add fields ==
        data["name"] = line.get('name') +' '+ line.get('last_name') if line.get('last_name') else line.get('name')
        # data["names"] = line.get('name')
        # data["last_name"] = line.get('last_name')
        data["l10n_latam_identification_type_id"] = type_doc_id.id
        data["vat"] = line.get('vat')
        data["email"] = line.get('email')
        data["phone"] = line.get('phone')
        data["mobile"] = line.get('mobile')
        data["street"] = line.get('street') if line.get('street') else ''
        data["company_type"] = line.get('company_type')
        
      
        values = {
            
            "data_text":data,
            "odoo_api_id":token.id,
            "response":response['detail']
        }

   
   
        customer_id = self.customer_exists(data["name"])
        if response['code'] == 200:
          
            if customer_id:
         
                customer_id.sudo().write(values)
                customer_id.sudo().post()
                response.update({'data':customer_id.partner_id})
               
            else:
                
                clientnew_id = customer_rest_api.sudo().create(values)
                clientnew_id.post()
                response.update({'data':clientnew_id.partner_id})   
            
        else:    
            customer_rest_api.sudo().create(values)
        return response    

    @http.route('/api/cliente', type='json', auth='public', cors="*")
    def api_client(self,**kwargs):
        
        if kwargs.get('token'):
            print("---->> si hay token")
            # return  {'status_code':400,'response':"Add 444token"}
        # if not kwargs.get('client'):
        #     return  {'status_code':400,'response':"Add Client"}
        odoo_rest_api = request.env["odoo.rest.api"]    
        token = odoo_rest_api.sudo().search([('account_token','=',kwargs.get('token'))], limit=1) 
        print("token", token)   
        # if not token:
        #     return  {'status_code':400,'response':"Invalid Token"}
        # response_client = []
        # for line in kwargs.get('client'):
        #     response_client = self.client_api_create(line,token)
        
        # if  response_client['code'] == 200:
        #     return {'status_code':200,'response':response_client['detail']}
           
        # else:
        #     return {'status_code':400,'response':response_client['detail']}
           











    # ===========================CREATE INVOICE ==========

    def invoice_exists(self,name_origin):
        account_move_api_id = request.env["account.move.rest.api"].sudo().search([('name','=',name_origin)], limit=1)
        if not account_move_api_id:
            return False
        return account_move_api_id

  
    
    def _prepare_invoice_vals(self,kwargs,company,token):
      
        response = {'code':200,'detail':'successful','data':''}
        client = kwargs.get('client')
        client_name = client['name']  +' '+  client['last_name'] if client['last_name'] else  client['name'] 
        cliente_obj = request.env["res.partner"].sudo().search([('name', '=', client_name)], limit=1)
        journal_obj = request.env["account.journal"].sudo().search([('type','=','sale'),('api_code', '=', kwargs.get('journal'))], limit=1)
        currency_obj = request.env["res.currency"].sudo().search([('name','=', kwargs.get('currency'))], limit=1)        
        payment_method = request.env["account.journal"].sudo().search([('type','in',['cash','bank']),('api_code', '=', kwargs.get('payment_methond'))], limit=1)
        # state_ebis = request.env["peb.shipping.status.sunat"].sudo().search([('code', '=', kwargs.get('state_ebis'))], limit=1)
        invoice_user_id =  request.env["res.users"].sudo().search([('name', '=',  kwargs.get('user'))], limit=1)
        message=''
        if not payment_method:
            message += "The payment method does not exist\n"
            response.update({'code':400,'detail': message})
        
        if not cliente_obj:
            client_new = self.client_api_create(client,token)
            cliente_obj =client_new['data']
           
 
        if not journal_obj:
            message += "The journal does not exist\n"
            response.update({'code':400,'detail': message})
        if not currency_obj:
            message += "The currency does not exist\n"
            response.update({'code':400,'detail': message})    

        lines_data_response = [(self._prepare_invoice_line(line)) for line in kwargs.get('detail')]
        line = []
        status=[]
         
        for line_invoice in lines_data_response:
            line.append(line_invoice['data'])
            if line_invoice['code']==400:
                status.append(400)

        if status:
          
            message += "The product does not exist \n"
            response.update({'code':400,'detail': message}) 
        vals = {
            "name": kwargs.get('origin'),
            "type": kwargs.get('type'),
            "communication":kwargs.get('payment_reference') if kwargs.get('payment_reference') else '' ,
            "partner_id": cliente_obj and cliente_obj.id,
            "currency_id": currency_obj and currency_obj.id or kwargs.get('currency'),
            "invoice_date": kwargs.get('invoice_date'),
            "invoice_date_due":kwargs.get('expiration_date'),
            "journal_id": journal_obj and journal_obj.id or kwargs.get('journal'),
            "company_id": company.id,
            "payment_method": payment_method.id,

        }
        # if state_ebis:
        #     vals.update({'shipping_status_sunat':state_ebis.id})
        if invoice_user_id:
            vals.update({'invoice_user_id':invoice_user_id.id})
        if not status:
            vals.update({'invoice_line_ids':line})
        response.update({'data':vals})

        return response               
    def _prepare_invoice_line(self, order_line):

        response = {'code':200,'detail':'successful','data':''}
        message =""
        try:
        
            # igv_affectation = request.env["peb.catalogue.07"].sudo().search([('code','=', order_line.get('tax'))],limit=1)
            # tax_obj=''
            # if igv_affectation:
            #     tax_obj = request.env["account.tax"].sudo().search([('type_tax_use','=','sale'),('igv_affectation','=',igv_affectation.id)],limit=1)
            producto_obj = request.env["product.product"].sudo().search([('name','ilike', order_line.get('product'))],limit=1)
            if not producto_obj:
                category_id = request.env["product.category"].sudo().search([('name','=', order_line.get('centro_costo'))],limit=1)
                pricelist_id = request.env["product.pricelist"].sudo().search([('api_code','=', order_line.get('cod_sede'))],limit=1)
                if category_id:
                    prod_vals={}
                    prod_vals['name']=order_line.get('product')
                    prod_vals['categ_id'] = category_id.id
                    if order_line.get('unidad_medida') == "SERVICIOS":
                        prod_vals['type'] = "service"
                    else:
                        prod_vals['type'] = "product"

                    producto_obj = request.env["product.product"].sudo().create(prod_vals)
                    if pricelist_id:
                        request.env["product.pricelist.item"].sudo().create({'compute_price':'fixed','applied_on':'0_product_variant','product_id':producto_obj.id,'pricelist_id':pricelist_id.id,'fixed_price':order_line.get('price_unit')})
                    
                else:
                    message += "The categoty does not exist \n"
                    response.update({'code':400,'detail': message})
                    
            price_unit = order_line.get('price_unit') if order_line.get('price_unit') else producto_obj.lst_price
            discount=0
            price_unit_total = price_unit * order_line.get('qty')
            if  order_line.get('discount_type')=="2" and order_line.get('discount')>0:

                discount_amount = price_unit_total /order_line.get('discount') if order_line.get('discount') else 0
                discount = 100/discount_amount
            else:
                discount = order_line.get('discount') if order_line.get('discount') else 0
            vals = {
                "product_id": producto_obj.id,
                "quantity": order_line.get('qty'),
                "discount": discount,
                "price_unit":price_unit,
                "name": producto_obj.display_name,
                # "tax_ids":tax_obj.ids if tax_obj else producto_obj.taxes_id.ids,
                "product_uom_id":producto_obj.uom_id.id,

            } 
            response.update({'data':vals})
            return response
        except: 
            if not message:
                message += "Error in the product lines"
                response.update({'code':400,'detail': message}) 
            return response   
    
    def api_account_move_code_200(self,move_vals,token):
    
        invoice_api_id = self.invoice_exists(move_vals['data']['name'])
        values = {
            "name":move_vals['data']['name'],
            "data_text":move_vals['data'],
            "odoo_api_id":token.id,
            "response":move_vals['detail']
        }
        
        if invoice_api_id:
            
            invoice_api_id.sudo().write(values)
            invoice_api_id.sudo().post()
        else:
            id_new = request.env["account.move.rest.api"].sudo().create(values)
            id_new.sudo().post()

    def api_account_move_code_400(self,move_vals,token):

        invoice_api_id = self.invoice_exists(move_vals['data']['name'])
        values = {
            "name":move_vals['data']['name'],
            "data_text":move_vals['data'],
            "odoo_api_id":token.id,
            "response":move_vals['detail']
        }
      
        if invoice_api_id:
            
            invoice_api_id.sudo().write(values)
            
        else:
            id_new = request.env["account.move.rest.api"].sudo().create(values)
                    

    @http.route('/api/invoice', type='json', auth='public', cors="*")
    def invoice_api_rest(self,**kwargs):
        if not kwargs.get('token'):
            return  {'status_code':400,'response':"Add token"}
        if not kwargs.get('invoice'):
            return  {'status_code':400,'response':"Add Client"}
        odoo_rest_api = request.env["odoo.rest.api"]    
        token = odoo_rest_api.sudo().search([('account_token','=',kwargs.get('token'))], limit=1)    
        if not token:
            return  {'status_code':400,'response':"Invalid Token"}
        
        # try:
        response = []
        company= request.env['res.company'].sudo().search([],limit =1)
        for inv in kwargs.get('invoice'):
    
            move_vals = self._prepare_invoice_vals(inv,company,token)
            if move_vals['code']==200:
                self.api_account_move_code_200(move_vals,token)
                
            else:
                self.api_account_move_code_400(move_vals,token)
                response.append({'invoice':move_vals['data']['name'],'detail':move_vals['detail']},)
                
        if response:
            return {'status_code':400,'response':'invoice no create','invoice':response}
        else:
    
            return   {'status_code':200,'response':'successfully created invoice'}
        # except:  
        #     return {'status_code':400,'response':'invoice not created, incorrect data,','invoice':response}  