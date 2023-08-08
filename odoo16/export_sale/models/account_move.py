# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_move(models.Model):
    _inherit = 'account.move'

    active_export_sale = fields.Boolean('activate export sales')

    @api.model
    @api.onchange('active_export_sale')
    def assing_type_operation_export_sale(self):
        
        for invoice in self:
            
            if invoice.active_export_sale:
                catalogue = self.env['peb.catalogue.51'].search([('code','=','0200')])
                invoice.update({'operation_type':catalogue})
            
            else:
                catalogue=self.env['peb.catalogue.51'].search([('code','=','0101')])
                invoice.update({'operation_type':catalogue})