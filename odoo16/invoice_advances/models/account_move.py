from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    advance_remaining_amount = fields.Float(string='Monto restante de Anticipo',compute='get_advance_amount', store=True)
    advance_amount = fields.Float(string='Monto Anticipo',compute='get_advance_amount')
    #is_advance =  fields.Boolean(string='Es Anticipo')
    
    
    @api.depends('amount_total')
    def get_advance_amount(self):
        for rec in self:
            rec.advance_amount = rec.amount_total
            invoices=rec.env['invoice.advance'].search([('invoice_id','=',rec.id)])
            total_advance=0.0
            if invoices:
                for inv in invoices:
                    total_advance+=inv.amount
            rec.advance_remaining_amount = rec.advance_amount - total_advance
            
    # @api.onchange('invoice_line_ids')
    # def onchange_total_advance(self):
    #     if self.amount_total:
    #         self.advance_remaining_amount= self.amount_total
    
    
#class AccountMove(models.Model):
#    _inherit = 'account.move.line'  
    
#    advance_invoice_id =  fields.Many2one(string='Factura anticipo', comodel_name='account.move')