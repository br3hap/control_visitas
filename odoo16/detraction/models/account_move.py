# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_move(models.Model):
    _inherit = 'account.move'

    active_detraction = fields.Boolean('Active detraction')
    service_detraction = fields.Many2one('peb.catalogue.service.spot','Service of detraction')
    type_operation_detraction = fields.Many2one('peb.catalogue.type.operation.detraction','Type Operation of Detraction')
    type_paid_detraction = fields.Many2one('peb.catalogue.paid.detraction','Type Paid of Detraction')
    active_round_amount = fields.Boolean('Active Round Amount Detraction')
    rate_detraction = fields.Float('Rate Detraction', compute='get_amount_detraction', default=0.00)
    amount_detraction = fields.Float('Amount Detraction', compute='get_amount_detraction', default=0.00)
    detraction_date = fields.Date('Date of Detraction')
    operation_number_detraction = fields.Char('Operation Number of Detraction')

    active_sale_auto_detraction = fields.Boolean('Autodetracción')

    @api.model
    @api.depends('invoice_line_ids','service_detraction', 'active_round_amount')
    def get_amount_detraction(self):
        
        for invoice in self:
            
            if invoice.invoice_line_ids:
                rate_detraction = 0.00
                
                if invoice.service_detraction:
                    rate_detraction = invoice.service_detraction.percentage
                    
                for line in invoice.invoice_line_ids:
                    product = line.product_id.product_tmpl_id
                    if product.service_detraction:
                        invoice.active_detraction = True
                        self.assing_type_operation()
                        if rate_detraction < product.service_detraction.percentage:
                            rate_detraction = product.service_detraction.percentage
                            invoice.service_detraction  = product.service_detraction.id
                            
                    elif product.categ_id.service_detraction:
                        invoice.active_detraction = True
                        self.assing_type_operation()
                        if rate_detraction < product.categ_id.service_detraction.percentage:
                            rate_detraction = product.categ_id.service_detraction.percentage
                            invoice.service_detraction  = product.categ_id.service_detraction.id
                    else:
                        invoice.amount_detraction = 0.00
                        invoice.rate_detraction = 0.00
                
                if invoice.active_round_amount:
                    invoice.amount_detraction = round((invoice.amount_total*rate_detraction/100), 0)
                else:
                    invoice.amount_detraction = round((invoice.amount_total*rate_detraction/100), 2)
                
                invoice.rate_detraction=float(rate_detraction)
            
            else:
                invoice.amount_detraction = 0.00
                invoice.rate_detraction = 0.00

    @api.model
    @api.onchange('active_detraction')
    def assing_type_operation(self):
        
        for invoice in self:
            
            if invoice.active_detraction:
                catalogue = self.env['peb.catalogue.51'].search([('code','=','1001')])
                invoice.update({'operation_type':catalogue})
            
            else:
                catalogue=self.env['peb.catalogue.51'].search([('code','=','0101')])
                invoice.update({'operation_type':catalogue})
    

    # @api.model
    def create(self, values):

        result = super(account_move, self).create(values)

        # EVALUAMOS SI ES DE ECOMMERCE
        if result.invoice_origin:
            result.get_amount_detraction()
                
        return result