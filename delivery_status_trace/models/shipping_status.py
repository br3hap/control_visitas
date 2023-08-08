from odoo import api, fields, models


class ShippingStatus(models.Model):
    _name = 'shipping.status'
    _description = 'Status Delivery Shipping'
    _order = 'sequence'

    name = fields.Char(string='Name')
    
    sequence = fields.Integer(string='Secuencia')
    
    
    color = fields.Integer(string='Color')
    
    active = fields.Boolean(string='Activo?',default=True)
    
    
