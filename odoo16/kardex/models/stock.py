# -*- coding: utf-8 -*-
from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def create(self, values):
        ids = super(StockPicking, self).create(values)

        if self._context:
            type_op = None
            if self._context.get('type_op_sale'):
                type_op = 1
            elif self._context.get('type_op_purchase'):
                type_op = 2
            if type_op:
                for sp in ids:
                    sp.write({'type_operation': type_op})

        return ids

    type_operation = fields.Many2one('peb.catalogue.12', string="Type of operation")
