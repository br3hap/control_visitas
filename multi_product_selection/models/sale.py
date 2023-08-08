# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SrMultiProduct(models.TransientModel):
    _name = 'sr.multi.product'

    product_ids = fields.Many2many('product.product', string="Product")

    def add_product(self):
        active_model = self._context.get('active_model')
        if active_model=='sale.order': 
            for line in self.product_ids:
                self.env['sale.order.line'].create({
                    'product_id': line.id,
                    'order_id': self._context.get('active_id')
                })
            return
        elif active_model=='account.move':
            for product in self.product_ids:
                invoice_id = self._context.get('active_id')
                product_name=""
                if product.default_code:
                    product_name = str(product.default_code + product.name) 
                else:
                    product_name= product.name 
                invoice_object = self.env['account.move'].search([('id','=',invoice_id)])
                tax_ids = []
                if invoice_object.move_type == 'out_invoice':
                    tax_ids.append(product.taxes_id.id)
                elif invoice_object.move_type == 'in_invoice':
                    tax_ids.append(product.supplier_taxes_id.id)
                     
                invoice_line={
                        'product_id': product.id,
                        'name': product_name,
                        'move_id':invoice_id,
                        'account_id':product.categ_id.property_account_income_categ_id.id,
                        'price_unit': product.list_price,
                        'quantity': 1.0,
                        'discount': False,
                        'product_uom_id': product.uom_id.id,
                        'tax_ids': [(6, 0, tax_ids)],
                        }
           
                self.env['account.move.line'].with_context(
            check_move_validity=False).create(invoice_line)
            return
