from odoo import api, fields, models


class ShippingVehicle(models.Model):
    _name = 'shipping.vehicle'
    _rec_name = 'plate_number'

    brand  = fields.Char(string='Brand')
    
    manufacture_year = fields.Integer(string='Manufacture Year')
    
    plate_number = fields.Char(string='Plate Number')
    
    partner_id = fields.Many2one(comodel_name='res.partner', string='Shipping Company')
    
    
    active = fields.Boolean(string='Active?',default=True)
    
    
    
    
    
    
