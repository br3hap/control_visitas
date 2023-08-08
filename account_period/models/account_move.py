# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError

class account_move(models.Model):
    _inherit = 'account.move'

    period_id = fields.Many2one('account.period', 'Period')

    # Para cada invoice se setea el periodo, de estar creado.
    # Sino, lanza mensaje impidiendo la creación por período no creado para la fecha indicada.
    # date cambiado por invoice_date, cambiado otra vez por date
    
    @api.model
    def create(self, values):
        # Validamos si existe periodo para esta fecha
        if 'invoice_date' in values.keys() and 'invoice_date' is not False:
            if not ('period_id' in values.keys()) or not values['period_id']:
                period = self.env['account.period']

                period_obj = period.search([('date_start', '<=',values['invoice_date']),
                                            ('date_stop', '>=',values['invoice_date'])],limit=1)
                
                if period_obj:
                    # Seteamos el Periodo
                    values['period_id'] = period_obj.id
                else:
                    raise ValidationError(_('There is no period created for the selected date'))
        
        result = super(account_move, self).create(values)
            
        return result
    
    @api.model
    def write(self, values):
        # Validamos si existe periodo para esta fecha
        if 'invoice_date' in values.keys():
            if not ('period_id' in values.keys()) or not values['period_id']:
                period = self.env['account.period']
                period_obj = period.search([('date_start', '<=',values['invoice_date']),
                                                ('date_stop', '>=',values['invoice_date'])],limit=1)
                if period_obj:
                    # Seteamos el Periodo
                    values['period_id'] = period_obj.id
                else:
                    raise ValidationError(_('There is no period created for the selected date'))
        
        result = super(account_move, self).write(values)
            
        return result