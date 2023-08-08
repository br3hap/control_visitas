# -*- coding: utf-8 -*-

from odoo import models, fields, api

class uom_uom(models.Model):
    _inherit = 'uom.uom'

    unit_measure_code = fields.Char('Unit of measure code')