# -*- coding: utf-8 -*-

from odoo import models, fields, api

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    anticipo_id = fields.Many2one('account.move', 'Anticipo')

    def _prepare_invoice_line(self, **optional_values):
        values = super(sale_order_line, self)._prepare_invoice_line(**optional_values)
        
        if self.anticipo_id:
            res['anticipo_id'] = self.anticipo_id
        return values