from odoo import models, fields, api, _
class ResPartener(models.Model):
    _inherit = 'res.partner'

    def _default_country(self):
        return self.env.company.country_id.id

    country_id = fields.Many2one(default=_default_country)