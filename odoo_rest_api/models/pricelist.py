from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    _sql_constraints = [('api_code_unique', 'unique(api_code)','already exists with this api code')]

    api_code =  fields.Char(string='API code')

    