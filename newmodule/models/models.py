# -*- coding: utf-8 -*-

# from odoo import models, fields, api

# class StockMoveLine(models.Model):
#     _inherit = 'stock.move.line'

#     name_stock = fields.Char('Nombre de Stock')


# class newmodule(models.Model):
#     _name = 'newmodule.newmodule'
#     _description = 'newmodule.newmodule'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
