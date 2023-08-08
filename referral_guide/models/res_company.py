from odoo import fields, models


class res_company(models.Model):
    _inherit = 'res.company'

    def _get_idetification_type(self):
        return self.env['l10n_latam.identification.type'].search([('l10n_pe_vat_code','=','6')],limit=1)

    identification_type_id = fields.Many2one('l10n_latam.identification.type',string="Tipo de Documento", default=_get_idetification_type)
    city_id = fields.Many2one('res.city', string='City of Address')
    district_id = fields.Many2one(
        'l10n_pe.res.city.district', string='District',
        help='Districts are part of a province or city.')

