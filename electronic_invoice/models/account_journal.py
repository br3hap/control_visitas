# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_journal(models.Model):
    _inherit = 'account.journal'

    active_ecletronic = fields.Boolean('Active Electronic Invoice')
    sunat_document_type = fields.Many2one('peb.catalogue.01', 'Sunat Document Type')
    sunat_document_type_related = fields.Many2one('peb.catalogue.01', 'Sunat Document Type')
    is_contg = fields.Boolean('Contigencia Electronica')
    almacen = fields.Many2one('stock.warehouse', 'Almacen')
   
