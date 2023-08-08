# -*- coding: utf-8 -*-
from odoo import models, fields


class stock_init_kardex(models.Model):
    _name='stock.init.kardex'
    
    product_id = fields.Many2one('product.product', string='Product', required=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True)
    month = fields.Integer(string='Month',digits=(2), required=True)
    year = fields.Integer(string='Year', digits=(4), required=True)
    stock_qty = fields.Float()
    positive_flow_qty = fields.Float()
    negative_flow_qty = fields.Float()
    
    _sql_constraints = [
            ('stock_kdx_period_uniq', 'UNIQUE (warehouse_id, product_id, year, month)', 'The stock of a product per store and product has to be unique.'),
    ]
