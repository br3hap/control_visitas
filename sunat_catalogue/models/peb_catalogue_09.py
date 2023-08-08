# -*- coding: utf-8 -*-

from odoo import models, fields, api


class peb_catalogue_09(models.Model):
    _name = 'peb.catalogue.09'
    _description = 'peb.catalogue.09'
    _rec_name="description"
    
    type_catalog = fields.Integer("Type", required=True)
    code = fields.Char("Code", required=True)
    description = fields.Char("Description", required=True)
    
    @api.depends('code', 'description')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name +=  table.description
            result.append((table.id, l_name ))
        return result
