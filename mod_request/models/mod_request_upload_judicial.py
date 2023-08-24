# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__) 

class mod_request_upload_judicial_purchased(models.Model):
    _name = 'mod.request.upload.judicial.purchased'
    _description = _("upload attachments purchased")

    mod_request_id = fields.Many2one('mod.request', string='Cod. Request')
    file_purchased = fields.Binary(string='File Purchased')
    file_name_purchased = fields.Char(string='File Name Purchased')
    date = fields.Datetime(string='Date',copy = False, default = lambda self: fields.datetime.now())
    state = fields.Boolean(string="Send", default=False)


class mod_request_upload_judicial_supported(models.Model):
    _name = 'mod.request.upload.judicial.supported'
    _description = _("upload attachments supported")


    _order = 'create_date desc'


    LIST_STATE = [
        ('in_progress', 'En Proceso'),
        ('completed', 'Completado')
    ]


    mod_request_id = fields.Many2one('mod.request', string='Cod. Request')
    file_supported = fields.Binary(string='File Supported')
    file_name_supported = fields.Char(string='File Name Supported')
    date = fields.Datetime(string='Date',copy = False, default = lambda self: fields.datetime.now())
    requirement_id = fields.Many2one('mod.request.requirements', context={'name_rq': True},)
    amount = fields.Float(string='Amount')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.uid)
    amount_remaining = fields.Float(string="Amount Remaining", compute='_compute_amount_remaining')
    state_line = fields.Selection(LIST_STATE, string = 'State' ,default='in_progress')
    description = fields.Text('Description')

    @api.onchange('requirement_id')
    def _onchange_amount(self):
        for rec in self:
            rec.amount = rec.requirement_id.amount_requirement

    @api.onchange('amount')
    def _compute_amount_remaining(self):
        for rec in self:
            rec.amount_remaining = rec.requirement_id.amount_requirement - rec.amount





    def action_completed(self):
        for rec in self:
            rec.write({'state_line':'completed'})
    
    def action_in_progress(self):
        for rec in self:
            rec.write({'state_line':'in_progress'})
            

            

    



