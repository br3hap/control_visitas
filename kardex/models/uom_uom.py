# -*- coding: utf-8 -*-
from odoo import models, fields


class uom_uom(models.Model):
    _inherit = 'uom.uom'
    
    kardex_code = fields.Char('Kardex code')