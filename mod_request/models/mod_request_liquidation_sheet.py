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

    LIST_STATE = [
        ('in_progress', 'In Process'),
        ('completed', 'Completed')
    ]


    name = fields.Char(string='Cod. Settlement', readonly=True, required=True, copy=False, default='New')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    user_id = fields.Many2one('res.users', string='Responsible')
    state = fields.Selection(LIST_STATE, string = 'State' ,default='in_progress')
    line_ids = fields.One2many('mod.request.liquidation.sheet.line','liquidation_sheet_id', string='Lines')
    currency_id = fields.Many2one('res.currency')
    total_amount = fields.Monetary(string='Total', compute='_compute_total_amount', currency_field='currency_id')


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
        self.write({'state':'completed'})

    def action_back(self):
        self.write({'state':'in_progress'})

