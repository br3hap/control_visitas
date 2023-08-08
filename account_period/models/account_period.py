# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import calendar


class account_period(models.Model):
    _name = 'account.period'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = _("Account period")
    # _rec_name = _("Account period")

    name = fields.Char("Name", required=True, tracking=True)
    code = fields.Char("Code", required=True, tracking=True)
    date_start = fields.Date("Date Start", required=True, tracking=True)
    date_stop = fields.Date("Date Stop", required=True, tracking=True)

    # close = fields.Boolean('Cerrado', default=False)
    state_desc = fields.Char('Status', compute='_compute_description_state')

    state = fields.Selection([
        ('open', 'Open'),
        ('close', 'Closed')
    ], string='Status', default='open', copy=False, index=True, readonly=True, store=True, tracking=True, help="Status of the period.")
    
    def _compute_description_state(self):
        for rec in self:
            if rec.state == 'open':
                rec.state_desc = _('Open')
            elif not rec.state == 'close':
                rec.state_desc = _('Closed')
            else:
                rec.state_desc = _('Closed')
    
    def open(self):
        for rec in self:
            if rec.state == 'close':
                rec.write({'state': 'open'})

    def close(self):
        for rec in self:
            if rec.state == 'open':
                rec.write({'state': 'close'})
    
    def unlink(self):
        for rec in self:
            if rec.state == 'close':
                raise UserError(_("You cannot delete periods that are closed."))
        return super(account_period, self).unlink()
        

class masive_creation_period(models.TransientModel):
    _name = 'masive.creation.period'
    
    fiscal_year = fields.Integer("Año", required=True, help='Año del cual se generarán sus periodos', default=2021)

    def ejecutar(self):
        # instancias
        period_obj = self.env['account.period']
        year = self.fiscal_year
        # Validamos si existe periodos creados para este año
        existe = period_obj.search([('name', 'like', str(year))])
        if existe:
            raise UserError(_("Existe periodos creados para este año fiscal"))
        else:
            # Realizamos las creaciones
            for i in range(1, 13):
                mes = str(i).zfill(2)
                code = mes+"/"+str(year)
                first_date = str(year)+'-'+mes+'-'+'01'
                last_date = str(year)+'-'+mes+'-'+str(calendar.monthrange(year,i)[1])
                
                val = {
                    'name': code,
                    'code': code,
                    'date_start': first_date,
                    'date_stop': last_date,
                    'state': 'open',
                }

                period_obj.create(val)


        
        
    