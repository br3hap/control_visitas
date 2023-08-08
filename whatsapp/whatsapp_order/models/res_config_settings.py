# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_enable_order = fields.Boolean(string='Order',default = True)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['whatsapp_enable_order'] = self.env['ir.config_parameter'].sudo().get_param('whatsapp_order.whatsapp_enable_order', default=False)
        return res

    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('whatsapp_order.whatsapp_enable_order', self.whatsapp_enable_order)
        super(ResConfigSettings, self).set_values()
