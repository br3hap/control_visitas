# -*- coding: utf-8 -*-

from odoo import models, fields, api 

class type_purcharse(models.Model):
    _inherit = 'purchase.order'
        
    type_purchase = fields.Selection(
        [('national', 'Nacional'),
         ('international', 'Internacional')],
        string="Tipo de compra", 
        readonly=False,
        default='national'
    )


class account_move(models.Model):
    _inherit = 'account.move'
        
    type_purchase = fields.Selection(
        [('national', 'Nacional'),
         ('international', 'Internacional')],
        string="Tipo de compra",
        compute='_compute_type_purchase', 
        store=True
    )


    @api.depends('invoice_origin')
    def _compute_type_purchase(self):
        for rec in self:  
            purchase_order = rec.env['purchase.order'].search([('name','=',rec.invoice_origin)], order='create_date asc',limit=1) 
                
            if len(purchase_order) == 1: 
                rec.type_purchase = purchase_order.type_purchase
            else:
                rec.type_purchase = None
            



