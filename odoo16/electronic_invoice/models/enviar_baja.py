# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, UserError


class account_move(models.Model):
    _inherit = 'account.move'

    def button_send_low(self):
        if self.amount_total != self.amount_residual:
            raise UserError(
                _('Primero debe Romper la Conciliacion de los pagos'))

        mod_obj = self.env['ir.model.data']

        view_ref = mod_obj.check_object_reference(
            'electronic_invoice', 'baja_form_view')
        view_id = view_ref and view_ref[1] or False

        id_activo = self.id

        logs_ids = []
        for so in self.env['bajas'].search([('invoice_id', '=', id_activo)]):
            logs_ids += [so.id]

        domain = "[('id','in',[" + ','.join(map(str, logs_ids)) + "])]"

        return {
            'type': 'ir.actions.act_window',
            'name': "Baja de Comprobante",
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'bajas',
            'target': 'new',
            'domain': domain,
            'context': {
                'invoice_id': self.id,
                'fecha_hora': fields.Datetime.now(),
            }
        }
