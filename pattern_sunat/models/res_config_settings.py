# -*- coding: utf-8 -*-

from odoo import api, fields, models
# MRamirez: se agrega en configuracion un flag para desabilitar la consulta al padron
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    active_pattern_sunat = fields.Boolean(default = True)    

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['active_pattern_sunat'] = self.env['ir.config_parameter'].sudo().get_param('pattern_sunat.active_pattern_sunat', default=False)
        return res

    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('pattern_sunat.active_pattern_sunat', self.active_pattern_sunat)
        super(ResConfigSettings, self).set_values()
