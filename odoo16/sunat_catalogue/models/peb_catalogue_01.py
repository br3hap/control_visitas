# -*- coding: utf-8 -*-

from odoo import models, fields, api


class peb_catalogue_01(models.Model):
    _name = 'peb.catalogue.01'
    _description = 'peb.catalogue.01'
    _rec_name="description"
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
