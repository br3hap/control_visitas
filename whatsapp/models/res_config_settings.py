# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_enable = fields.Boolean(default = False, string='enable whatsapp')
    whatsapp_api_url = fields.Char(string='Url',default="https://api.whatsapp.com/send?phone=")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['whatsapp_enable'] = self.env['ir.config_parameter'].sudo().get_param('whatsapp.whatsapp_enable', default=False)
        res['whatsapp_api_url'] = self.env['ir.config_parameter'].sudo().get_param('whatsapp.whatsapp_api_url', default='https://api.whatsapp.com/send?phone=')
        return res

    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('whatsapp.whatsapp_enable', self.whatsapp_enable)
        self.env['ir.config_parameter'].sudo().set_param('whatsapp.whatsapp_api_url', self.whatsapp_api_url)
        super(ResConfigSettings, self).set_values()
