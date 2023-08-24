# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero
from datetime import date
from datetime import datetime
from odoo.tools.misc import clean_context, format_date
import logging
_logger = logging.getLogger(__name__) 

class mod_request_liquidation_sheet(models.Model):

    _name = 'mod.request.liquidation.sheet'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'analytic.mixin']
    _description = _("Liquidation Sheet")

    _order = 'create_date desc'

    LIST_STATE = [
        ('in_progress', 'En Proceso'),
        ('completed', 'Completado')
    ]


    name = fields.Char(string='Cod. Settlement', required=True, copy=False, default='New')
    description = fields.Char(string='Descripcion', default='Informe de Liquidación')
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    state = fields.Selection(LIST_STATE, string = 'State' ,default='in_progress')
    line_ids = fields.One2many('mod.request.liquidation.sheet.line','liquidation_sheet_id', string='Lines')
    currency_id = fields.Many2one('res.currency')
    total_amount = fields.Monetary(string='Total', compute='_compute_total_amount', currency_field='currency_id')
    date = fields.Datetime(string='Date',copy = False, default = lambda self: fields.datetime.now())
    observation = fields.Text(string='Observation')
    amount_total = fields.Monetary(string="Amount", compute='_compute_amounts', tracking=4)


    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id,'%s / %s' % (rec.description, rec.name)))
        return result


    @api.depends('line_ids.amount')
    def _compute_amounts(self):
        for rec in self:
            rec.amount_total = rec.total_amount

    


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('mod.request.liquidation') or 'New'
        result = super(mod_request_liquidation_sheet, self).create(vals)
        return result
    

    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        for line in self:
            line.total_amount = sum(line.line_ids.mapped('amount'))

    
    def action_completed(self):
        for rec in self:
            for line in rec.line_ids:
                line.state_line = 'completed'
        self.write({'state':'completed'})

    def action_back(self):
        for rec in self:
            for line in rec.line_ids:
                line.state_line = 'in_progress'
        self.write({'state':'in_progress'})

