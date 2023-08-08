# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class account_move(models.Model):
    _inherit = 'account.move'

    def action_rellenar_cuotas(self):

        return {
            'name': _('Rellenar Cuotas'),
            'res_model': 'rellenar.cuotas',
            'view_mode': 'form',
            'view_id': self.env.ref('auto_cuotas.view_rellenar_cuotas_form').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


class rellenar_cuotas(models.TransientModel):
    _name = 'rellenar.cuotas'
    _description = 'Rellenar Cuotas'

    tipo_cuotas = fields.Selection(selection=[
        ('01', '1 Cuota'),
        ('02', 'Mas de una Cuota')
    ], string='Cuotas', required=True, default='01')

    numero_cuotas = fields.Integer('Número de Cuotas')

    def validar(self):

        contexto = self.env.context

        cuotas = self.env['cuotas']

        if contexto['active_model']=='account.move':
            invoice = self.env['account.move'].browse(contexto['active_id'])
        else:
            invoice = self.env['account.move'].search([('invoice_origin', '=', contexto['default_invoice_origin'][0])])


        monto = 0.00

        if invoice.active_detraction:
            monto = invoice.amount_total-invoice.amount_detraction
        elif  invoice.active_retencion:
            monto = invoice.amount_total-invoice.amount_retencion      
        else:
            monto = invoice.amount_total

        if self.tipo_cuotas == '01':
            data = {
                'name': 'Cuota001',
                'amount': monto,
                'date': invoice.invoice_date_due,
                'move_id':  invoice.id,
            }

            cuotas.create(data)
        else:
            sum_acumulado = 0
            monto_2 = round((monto/self.numero_cuotas), 2)
            for seq in range(self.numero_cuotas):

                name = 'Cuota00'+str(seq+1)                

                if seq+1 == self.numero_cuotas:
                    monto = round((monto - sum_acumulado), 2)
                    data = {
                        'name': name,
                        'amount': monto,
                        'date': invoice.invoice_date_due,
                        'move_id':  invoice.id,
                    }

                else:
                    data = {
                        'name': name,
                        'amount': monto_2,
                        'date': invoice.invoice_date_due,
                        'move_id':  invoice.id,
                    }
                
                sum_acumulado = sum_acumulado+monto_2

                cuotas.create(data)

        return True
