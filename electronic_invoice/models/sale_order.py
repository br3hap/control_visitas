from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, UserError

class sale_order(models.Model):
    _inherit='sale.order'

    observaciones = fields.Char('Observaciones')