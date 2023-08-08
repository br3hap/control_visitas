# -*- coding: utf-8 -*-

from odoo import models, fields, api


class peb_catalogue_paid_detraction(models.Model):
    _name = 'peb.catalogue.paid.detraction'
    _description = 'peb.catalogue.paid.detraction'
    _rec_name="description"
    
    code = fields.Char("Code", required=True)
    description = fields.Char("Description", required=True)
    
    # @api.model
    # @api.depends('code', 'description')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name +=  table.description
            result.append((table.id, l_name ))
        return result