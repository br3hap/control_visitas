from odoo import api, fields, models


class SettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_shipping_trace = fields.Boolean(string='Permitir Seguimiento de Pedido')
    
    
    def set_values(self):
        res = super(SettingsInherit, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('delivery_status_trace.allow_shipping_trace', self.allow_shipping_trace)
        return res
    
    @api.model
    def get_values(self):
        res = super(SettingsInherit, self).get_values()
        allow_shipping_trace = bool(self.env['ir.config_parameter'].sudo().get_param('delivery_status_trace.allow_shipping_trace'))
        res.update({
            'allow_shipping_trace' : allow_shipping_trace,
            })
        return res
    
    
