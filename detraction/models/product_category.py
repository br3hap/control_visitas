# -*- coding: utf-8 -*-

from odoo import models, fields, api


class product_category(models.Model):
    _inherit = 'product.category'

    service_detraction = fields.Many2one('peb.catalogue.service.spot','Servicio de Detracción')