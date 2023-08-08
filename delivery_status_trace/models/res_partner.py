from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    carrier_ids = fields.One2many(comodel_name='res.partner', inverse_name='delivery_company_id', string='Carriers')
    
    delivery_company_id = fields.Many2one(comodel_name='res.partner', string='Delivery Company')
    
    vehicle_ids = fields.One2many(comodel_name='shipping.vehicle', inverse_name='partner_id', string='Vehicles')
        
    is_delivery_company = fields.Boolean(string='Delivery Company?',default=False)
    
    
    lincence_file = fields.Binary(string='License File')
    
