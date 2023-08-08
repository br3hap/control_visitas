# -*- coding: utf-8 -*-

from odoo.osv import osv, expression
from odoo import models, fields, api, _
       
class ir_sequence(models.Model):
    _inherit='ir.sequence'
    
    warehouse_id = fields.Many2one('stock.warehouse','Almacen')