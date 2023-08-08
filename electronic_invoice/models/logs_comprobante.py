# -*- coding: utf-8 -*-

from odoo import models, fields, _

class logs_comprobante(models.Model):
    _name = 'logs.comprobante'
    _description = 'logs.comprobante'
    _order = 'fecha,id'

    invoice_id = fields.Many2one('account.move', readonly=True)
    fecha = fields.Datetime(string='Fecha')
    descripcion = fields.Char('Descripción')
    estado_ini = fields.Char('Estado Inicial')
    estado_fin = fields.Char('Estado Final')
    descripcion_detallada = fields.Text("Descripción Detallada")