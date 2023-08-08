# -*- coding: utf-8 -*-

from odoo import models, fields, api


class peb_shipping_status_sunat(models.Model):
    _name = 'peb.shipping.status.sunat'
    _description = 'peb.shipping.status.sunat'
    _rec_name="description"
    
    code = fields.Char("Code", required=True)
    name = fields.Char("Name", required=True)
    description = fields.Char("Description", required=True)
    
    @api.depends('code', 'description', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name +=  table.name
            result.append((table.id, l_name ))
        return result
