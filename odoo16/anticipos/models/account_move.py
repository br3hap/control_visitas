# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_move(models.Model):
    _inherit = 'account.move'

    anticipo = fields.Boolean('Anticipo')

class account_move_line(models.Model):
    _inherit = 'account.move.line'

    anticipo_id = fields.Many2one('account.move', 'Anticipo ID')