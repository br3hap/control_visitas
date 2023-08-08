# -*- coding: utf-8 -*-

from odoo import models, fields, _

class mensaje_emergente(models.TransientModel):
    _name="mensaje.emergente"
    _description = 'mensaje.emergente'
    tipo = fields.Char('Tipo', default = lambda self: self._context.get('tipo', False), readonly=True)
    mensaje = fields.Char('Mensaje', default = lambda self: self._context.get('mensaje', False), readonly=True)
    mensaje_detallado = fields.Char('Mensaje Detallado', default = lambda self: self._context.get('mensaje_detallado', False), readonly=True)
    
    def get_mensaje(self, tipo=False, mensaje=False, mensaje_detallado=False):
        mod_obj = self.env['ir.model.data']
        view_ref = mod_obj.check_object_reference('electronic_invoice', 'mensaje_emergente_view')
        view_id = view_ref and view_ref[1] or False
        domain = "[]"
        return {
                'type': 'ir.actions.act_window',
                'name':"Mensaje",
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'mensaje.emergente',
                'view_id': False,
                'views': [(view_id, 'form')],
                'target': 'new',
                'nodestroy': True,
                'domain': domain,
                'context': {
                    'tipo' : _(tipo or ''),
                    'mensaje' : _(mensaje or ''),
                    'mensaje_detallado': _(mensaje_detallado or ''),
                }
            }