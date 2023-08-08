# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_move(models.Model):
    _inherit = 'account.move'

    operation_type = fields.Many2one('peb.catalogue.51', 'Type Operation')