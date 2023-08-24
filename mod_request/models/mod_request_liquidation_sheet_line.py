# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero
from datetime import date
from datetime import datetime
from odoo.tools.misc import clean_context, format_date
import logging
_logger = logging.getLogger(__name__) 

class mod_request_liquidation_sheet_line(models.Model):

    _name = 'mod.request.liquidation.sheet.line'
    _description = _("Liquidation Sheet Line")


    LIST_STATE = [
        ('in_progress', 'En Proceso'),
        ('completed', 'Completado')
    ]


    liquidation_sheet_id = fields.Many2one('mod.request.liquidation.sheet', string='Cod. Liquidation', ondelete='cascade')
    request_id = fields.Many2one('mod.request',string='Cod. Request', ondelete='cascade')
    name = fields.Char(string='Cod. Requirement')
    case = fields.Char(string='Case')
    proceedings = fields.Char(string='Proceedings')
    amount = fields.Float(string='Amount')
    date = fields.Datetime(string='Date',copy = False, default = lambda self: fields.datetime.now())
    court_entity = fields.Char(string='Court / Entity')
    ruc_dni = fields.Char(string='RUC / DNI')
    description = fields.Char(string='Description')
    partner_id = fields.Many2one('res.partner', string='Partner')
    state_line = fields.Selection(LIST_STATE, string = 'State' ,default='in_progress')


    def action_completed(self):
        for rec in self:
            rec.write({'state_line':'completed'})
    
    def action_in_progress(self):
        for rec in self:
            rec.write({'state_line':'in_progress'})
    







