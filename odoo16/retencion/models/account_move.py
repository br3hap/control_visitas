# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_move(models.Model):
    _inherit = 'account.move'

    active_retencion = fields.Boolean('Retencion')
    porcentaje_retencion = fields.Selection([('01','3%'), ('02', '8%')])
    amount_retencion = fields.Float('Monto Retencion', compute='get_amount_retencion', default=0.00)

    @api.model
    @api.depends('invoice_line_ids','porcentaje_retencion')
    def get_amount_retencion(self):
        
        for invoice in self:
            
            if invoice.invoice_line_ids:
                rate_detraction = 0.00
                if invoice.porcentaje_retencion:
                    if invoice.porcentaje_retencion == '01':
                        rate_detraction = 3
                    elif invoice.porcentaje_retencion == '02':
                        rate_detraction = 8
                    invoice.amount_retencion = round((invoice.amount_total*rate_detraction/100), 2)
                else:
                    invoice.amount_retencion = 0.00
                
            else:
                invoice.amount_retencion = 0.00