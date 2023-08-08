# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date, timedelta

class mod_request_masive_paid(models.TransientModel):
    
    _name='mod.request.masive.paid'

    journal_id = fields.Many2one('account.journal', 'Diario', required = True)
    account_id = fields.Many2one('account.account', 'Cuenta Destino', required = True)
    date = fields.Date('Fecha', required = True)
    memo = fields.Char('Memo', required = True)
    amount = fields.Float('Monto', required = True)
    partner_id = fields.Many2one('res.partner', 'Persona Asignada', required=True)

    def _get_payment_vals(self):
        """ Hook for extension """
        payment_methods = self.journal_id.outbound_payment_method_line_ids
        payment_method_id = payment_methods and payment_methods[0] or False

        return {
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'partner_id': self.partner_id.id,
            'journal_id': self.journal_id.id,
            'company_id': self.journal_id.company_id.id,
            'payment_method_line_id': payment_method_id.id if payment_method_id else False,
            'amount': self.amount,
            'currency_id': self.journal_id.currency_id.id or self.journal_id.company_id.currency_id.id,
            'date': self.date,
            'ref': self.memo,
            'state': 'draft',
            'destination_account_id': self.account_id.id
        }

    def execute_paid(self):

        # REALIZAMOS EL PAGO
        payment = self.env['account.payment'].create(self._get_payment_vals())
        payment.action_post()

        for solicitud in self.env['mod.request'].browse(self._context.get('active_domain')):
            if solicitud.type_request == 'judicial':
                if solicitud.process_request == 'repayment':
                    solicitud.action_complete()
                else:
                    solicitud.action_subscriber()
            else:
                solicitud.action_complete()
            # solicitud.state='subscriber'
            solicitud.payment_id = payment.id
            solicitud.num_operation = self.memo