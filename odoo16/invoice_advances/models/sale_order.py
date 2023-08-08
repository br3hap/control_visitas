from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    invoice_advance_ids = fields.One2many('invoice.advance', 'sale_id', string='invoice advance')
    is_advance_invoice =  fields.Boolean(string='Usar Facturas de Anticipos')
    
   
 
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    advance_invoice_id =  fields.Many2one(string='Factura', comodel_name='account.move')
    
    def _prepare_invoice_line(self, **optional_values):
        values = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if self.advance_invoice_id:
            values['anticipo_id']= self.advance_invoice_id.id    
        return values
    