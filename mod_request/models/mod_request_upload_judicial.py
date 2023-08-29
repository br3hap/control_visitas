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
    number_doc = fields.Char('Number Doc')
    

    @api.onchange('amount')
    def _compute_amount_remaining(self):
        for rec in self:
            rec.amount_remaining = rec.requirement_id.amount_requirement - rec.amount

    @api.onchange('requirement_id')
    def _onchange_amount(self):
        for rec in self:
            rec.amount = rec.requirement_id.qty_sin_sustentar


    # def write(self, vals):
    #     res = super(mod_request_upload_judicial_supported, self).write(vals)
    #     for r in self.requirement_id:
    #         if self.amount > r.qty_sin_sustentar:
    #             raise UserError('Es mayor es edicion')

    #     return res
    
    # def create(self, vals):
    #     env_requirement = self.env['mod.request.requirements']
    #     amount = env_requirement.search([('id','=',self.requirement_id.id)]).qty_sin_sustentar
    #     if self.amount > amount:
    #         raise UserError('Es mayor es creacio')

    #     res = super(mod_request_upload_judicial_supported, self).create(vals)
    #     # amount = env_requirement.search([('id','=',res.requirement_id.id)]).qty_sin_sustentar
    #     _logger.warning('res', res.amount,res.requirement_id.id, amount)

    #     # if res.amount > amount:
    #     #     raise UserError('Es mayor es creacio')

    #     return res




    def action_completed(self):
        for rec in self:
            if rec.amount_remaining < 0.00:
                raise UserError('el monto restante es negativo')
            rec.write({'state_line':'completed'})
    
    def action_in_progress(self):
        for rec in self:
            rec.write({'state_line':'in_progress'})
            

            

    



