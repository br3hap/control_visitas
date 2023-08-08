from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
import time
class InvoiceAdvance(models.Model):
    _name = 'invoice.advance'

    @api.model
    def _default_product_id(self):
        product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
        return self.env['product.product'].browse(int(product_id)).exists()
    @api.model
    def _default_deposit_account_id(self):
        return self._default_product_id().property_account_income_id
    @api.model
    def _default_deposit_taxes_id(self):
        return self._default_product_id().taxes_id
    
    @api.model
    def _default_partner(self):
        
        return self.sale_id.partner_id.id
    
    
    name = fields.Char(string='Descripcion')
    amount = fields.Float(string='Monto')
    percentage =  fields.Float(string='Porcentaje')
    
    sale_id = fields.Many2one(string='Venta', comodel_name='sale.order')
    partner_id =  fields.Many2one(string='Cliente', comodel_name='res.partner', related='sale_id.partner_id')
    # invoice_id =  fields.Many2one(string='Factura Anticipo', comodel_name='account.move', domain=['&','&','&',('state', '=', 'posted'), ('partner_id', '=', _default_partner),('advance_remaining_amount','>',0.0),('anticipo','=',True)])
    invoice_id =  fields.Many2one(string='Factura Anticipo', comodel_name='account.move')
    confirmed =  fields.Boolean(string='Confirmado')
    product_id = fields.Many2one('product.product', string='Down Payment Product', domain=[('type', '=', 'service')],
        default=_default_product_id)
    deposit_account_id = fields.Many2one("account.account", string="Income Account", domain=[('deprecated', '=', False)],
        help="Account used for deposits", default=_default_deposit_account_id)
    deposit_taxes_id = fields.Many2many("account.tax", string="Customer Taxes", help="Taxes used for deposits", default=_default_deposit_taxes_id)
    
    
    advance_remaining_amount = fields.Float(string='Monto restante de Anticipo')

    @api.onchange('name')
    def onchange_invoice_list(self):
        return {'domain': {'invoice_id': ['&','&','&',('partner_id', '=', self.sale_id.partner_id.id),('advance_remaining_amount','>',0),('anticipo','=',True),('state', '=', 'posted')]}}
    
    @api.onchange('invoice_id')
    def onchange_invoice_id(self):
        if self.invoice_id:
            
            self.advance_remaining_amount = self.invoice_id.advance_remaining_amount
    
    def _prepare_so_line(self, order, analytic_line_ids, tax_ids, amount):
        context = {'lang': order.partner_id.lang}
        so_values = {
            'name':  _('%s: %s') % ( self.name,time.strftime('%m %Y'),),
            'price_unit': -abs(amount),
            'product_uom_qty': 1,
            'order_id':order.id,
            'advance_invoice_id': self.invoice_id.id,
            # 'qty_invoiced':1,
            'discount': 0.0,
            'product_uom': self.product_id.uom_id.id,
            'product_id': self.product_id.id,
            'analytic_line_ids': analytic_line_ids,
            'tax_id': [(6, 0, tax_ids)],
            # 'is_downpayment': True,
          
        }
        del context
        print("##so_vals",so_values)
        return so_values
    
    def confirm_advance(self):
        sale_line_obj = self.env['sale.order.line']
        order = self.sale_id
        if not self.invoice_id:
           raise UserError('Agregue una Factura')
        
        if not self.amount:
           raise UserError('Ingrese un monto de Anticipo')
        if not self.product_id:
            vals = self._prepare_deposit_product()
            self.product_id = self.env['product.product'].create(vals)
            self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)
        
        if self.product_id.invoice_policy != 'order':
            raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
        if self.product_id.type != 'service':
            raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
        taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
        if order.fiscal_position_id and taxes:
            tax_ids = order.fiscal_position_id.map_tax(taxes).ids
        else:
            tax_ids = taxes.ids
        analytic_line_ids = []
        for line in order.order_line:
            analytic_line_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_line_ids]
        so_line_values = self._prepare_so_line(order, analytic_line_ids, tax_ids, self.amount)
        so_line = sale_line_obj.create(so_line_values)
        self.confirmed=True
        self.invoice_id.advance_remaining_amount = self.invoice_id.advance_remaining_amount - self.amount
    
    def _prepare_deposit_product(self):
        return {
            'name': 'Down payment',
            'type': 'service',
            'invoice_policy': 'order',
            'property_account_income_id': self.deposit_account_id.id,
            'taxes_id': [(6, 0, self.deposit_taxes_id.ids)],
            'company_id': False,
        }     