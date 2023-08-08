# -*- coding: utf-8 -*-

from odoo import models, fields, _

class logs_baja(models.Model):
    _name = 'logs.baja'
    _description = 'logs.baja'
    _order = 'fecha,id'
    
    baja_id = fields.Many2one('bajas', readonly=True)
    fecha = fields.Datetime(string='Fecha')
    descripcion = fields.Char('Descripción')
    estado_ini = fields.Char('Estado Inicial')
    estado_fin = fields.Char('Estado Final')
    descripcion_detallada = fields.Text("Descripción Detallada")