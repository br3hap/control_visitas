from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, UserError

class stock_picking(models.Model):
    _inherit='stock.picking'

    observaciones = fields.Text('Observaciones')

    # @api.model
    def create(self, vals):
        result = super(stock_picking, self).create(vals)
        if result.origin:
            orden_venta = self.env['sale.order'].search([('name', '=', result.origin)])
            if orden_venta:
                result.update({'observaciones':orden_venta.observaciones})
            
        return result
