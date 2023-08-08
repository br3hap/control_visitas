# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_enable_crm = fields.Boolean(string='CRM',default = True)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['whatsapp_enable_crm'] = self.env['ir.config_parameter'].sudo().get_param('whatsapp_crm.whatsapp_enable_crm', default=False)
        return res

    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('whatsapp_crm.whatsapp_enable_crm', self.whatsapp_enable_crm)
        super(ResConfigSettings, self).set_values()
