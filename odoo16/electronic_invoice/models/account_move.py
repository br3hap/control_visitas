# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, UserError

is_reverse = None


class account_move(models.Model):
    _inherit = 'account.move'

    @api.model
    def _default_shipping_status_sunat(self):
        return self.env['peb.shipping.status.sunat'].search([('code','=',1)], limit=1)
    shipping_status_sunat = fields.Many2one(
        'peb.shipping.status.sunat', 'Shipping Status to Sunat', copy=False)
    
    field_pdf = fields.Char('Name Pdf',  copy=False)
    file_data = fields.Binary('Dowlonad Pdf EBIS',  copy=False)
    
    field_xml = fields.Char('Name Xml',  copy=False)
    file_data_xml = fields.Binary('Dowlonad Xml EBIS',  copy=False)
    
    not_active_get_print_invoice = fields.Boolean('Active Invoice Print',  copy=False)

    observaciones = fields.Text('Observaciones')
    codigo_compra = fields.Char('Orden de Compra')
    tipo_pago = fields.Many2one('tipo.pago', 'Tipo de Pago')

    # EL botón post que sale en el comprobante
    def action_post(self):
       result = super(account_move, self).action_post()
       if self.journal_id.active_ecletronic:
           self.send_invoice()
       return result
    
    # metodo que se llama desde ecommerce para la generacion de asiento y posteo
    def post(self):
        # DNINACO RECORREMOS CADA SELF
        for move in self:
            # MRamirez
            # Inicio: Se valida si es reverse
            global is_reverse
            if is_reverse:
                is_reverse = None
                return
            result = super(account_move, move).post()
            # Fin

            if move.journal_id and not move.shipping_status_sunat:
                for journal in move.journal_id:
                    if journal.active_ecletronic:
                        move.send_invoice()
        return True
    
    @api.model_create_multi
    def create(self, values):
        result = super(account_move, self).create(values)
        for value in result:
            if value.move_type in ('out_invoice', 'out_refund'):

                if not value.operation_type:
                    catalogue = self.env['peb.catalogue.51'].search([('code','=','0101')])
                    value.update({'operation_type':catalogue})
            
            if value.invoice_origin:
                orden_venta = self.env['sale.order'].search([('name', '=', value.invoice_origin)])
                if orden_venta:
                    value.update({'observaciones':orden_venta.observaciones})
            
        return result
    
    # para validar que no este en proceso de baja 
    def action_invoice_register_payment(self):
        if self.shipping_status_sunat:
            if self.shipping_status_sunat.code in ('7','9','10'):
                raise UserError(_('No se debe pagar comprobantes en (proceso de baja, anulado, rechazado sunat)'))

        result = super(account_move, self).action_invoice_register_payment()
        return result
    
    @api.onchange('invoice_date')
    def _onchange_invoice_date(self):
        if self.invoice_date:
            if not self.invoice_payment_term_id and not self.invoice_date_due:
                self.invoice_date_due = self.invoice_date
            self.date = self.invoice_date
            # self._onchange_currency()
             #en odoo16 fue remplazado por _compute_currency_id
# MRamirez
# se agrega la variable global para evitar publicar las facturas rectificativas del btn reverse
class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def reverse_moves(self):
        global is_reverse
        is_reverse = True
        return super(AccountMoveReversal, self).reverse_moves()

