# -*- coding: utf-8 -*-

from odoo import models, fields, api

class stock_warehouse(models.Model):
    _inherit = 'stock.warehouse'

    warehouse_annex_code = fields.Char('Warehouse Annex Code')