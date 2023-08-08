from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"
    
    reason_id =  fields.Many2one(string='Motivo', comodel_name='peb.catalogue.09')

    
    
    def _prepare_default_reversal(self,move):
        res = super(AccountMoveReversal, self)._prepare_default_reversal(move)
        res.update({
            'reason': self.reason_id.id,
            'sustain':self.reason,
            'date_related_document':move.invoice_date,
            'related_document':move.name,
            'related_document_type':move.journal_id.sunat_document_type.code
       
        })
        return res 
        