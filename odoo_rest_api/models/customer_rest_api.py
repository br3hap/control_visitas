# -*- coding: utf-8 -*-
from unicodedata import name
from urllib import response
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import json
class CustomerResApi(models.Model):
    _name = 'customer.rest.api'

    name = fields.Char(string='name')
    succes = fields.Boolean(strign="Succes")
    data_text = fields.Text(string="Json")
    response = fields.Text(string="Response")
    odoo_api_id = fields.Many2one(string='Odoo Api', comodel_name='odoo.rest.api')
    partner_id = fields.Many2one(string='Client', comodel_name='res.partner')
    def post(self):
        for rec in self:
            
            str_data = rec.data_text.replace("\'", "\"")
            res_partner = json.loads(str_data)
            exist_partner_id = rec.env['res.partner'].search([('name','=',res_partner['name'])])
            message =""
            if exist_partner_id:
                exist_partner_id.write(res_partner)
                rec.partner_id=exist_partner_id.id
                message+= "the client %s was successfully created"%(exist_partner_id.name)

            else:
                id_new =rec.env['res.partner'].create(res_partner)
                rec.partner_id=id_new.id
                message += "the client %s was successfully created"%(id_new.name)
            rec.succes = True
            
            return message
           
            
    
    def udapte(self,partner_id):
        for rec in self:
            str_data = rec.data_text.replace("\'", "\"")
            res_partner = json.loads(str_data)
            id_new = rec.env['res.partner'].browse(partner_id)
            id_new.write(res_partner)
            message = "the client %s was successfully created"%(id_new.name)
            return message
                      
