# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class recibir_comprobante_pago_respuesta(models.TransientModel):
    _name='recibir.comprobante.pago.respuesta'
    
    indicadorResultado = fields.Char('Indicador Resultado', default = lambda self: self._context.get('indicadorResultado', False), readonly=True)
    mensaje = fields.Char('Mensaje', default = lambda self: self._context.get('mensaje', False), readonly=True)
