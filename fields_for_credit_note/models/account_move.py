# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, UserError

class account_move(models.Model):
    _inherit = 'account.move'

    reason = fields.Many2one('peb.catalogue.09', 'Reason',domain = [('type_catalog','=',3)]) #domain = [('tipo','=',3)]
    sustain = fields.Text('Sustain')
    related_document_type = fields.Selection([('01', 'invoice'),
                                              ('03', 'ballot')], 'Related Document Type')
    related_document = fields.Char('Related Document')
    date_related_document = fields.Date('Date of Related Document')
    type_voucher = fields.Many2one('peb.catalogue.10', 'Type Voucher')

    serie = fields.Char('Serie')
    correlativo = fields.Char('Correlativo')
    anho_dua = fields.Char('Año DUA')

    @api.constrains("type_voucher")
    def validar_documento_referencia(self):
        if self.type_voucher:
            
            if self.type_voucher.code in ['01', '03', '07', '08']:
                if not self.serie:
                    raise UserError(_('Se debe ingresar la serie'))
                if not self.correlativo:
                    raise UserError(_('Se debe ingresar correlativo'))
            
            if self.type_voucher.code in ['50']:
                if not self.anho_dua:
                    raise UserError(_('Se debe ingresar el Año de la DUA'))
    
    @api.constrains('ref', 'move_type', 'partner_id', 'journal_id', 'invoice_date')
    def _check_duplicate_supplier_reference(self):
        valores = True

    
    @api.depends('name', 'ref')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.name and table.name

            if table.serie:
                l_name +=  "("
                l_name +=  table.serie
                if not table.correlativo:
                    l_name +=  ")"

            if table.correlativo:
                if table.serie:
                    l_name +=  "-"
                else:
                    l_name +=  "("
                l_name +=  table.correlativo
                l_name +=  ")"
            
            if not table.serie and  not table.correlativo:
                if table.ref:
                    l_name +=  "("
                    l_name +=  table.ref
                    l_name +=  ")"

            result.append((table.id, l_name ))

        return result
            
