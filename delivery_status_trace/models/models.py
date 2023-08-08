# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class delivery_status_trace(models.Model):
#     _name = 'delivery_status_trace.delivery_status_trace'
#     _description = 'delivery_status_trace.delivery_status_trace'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
