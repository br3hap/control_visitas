# -*- coding: utf-8 -*-

from odoo import fields, models


class product_template(models.Model):
    _inherit = "product.template"

    sunat_code = fields.Char(string="Código SUNAT")