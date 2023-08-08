# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class AccountDebitNote(models.TransientModel):

    _inherit = 'account.debit.note'
    
    reason_id =  fields.Many2one(string='Motivo', comodel_name='peb.catalogue.09')
    
    def _prepare_default_values(self, move):

        res = super(AccountDebitNote, self)._prepare_default_values(move)
        res.update({
            'reason': self.reason_id.id,
            'sustain':self.reason,
            'is_note_document':True,
            'date_related_document':move.invoice_date,
            'related_document':move.name,
            'related_document_type':move.journal_id.sunat_document_type.code
       
        })
        return res 