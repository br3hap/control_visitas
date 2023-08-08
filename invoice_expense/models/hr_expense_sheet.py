# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero
from datetime import date
from datetime import datetime
from odoo.tools.misc import clean_context, format_date
import logging
_logger = logging.getLogger(__name__) 

class hr_expense_sheet(models.Model):

    _name = 'hr.expense.sheet'
    _inherit = 'hr.expense.sheet'

    invoice_expense_ids = fields.One2many('invoice.expense', 'expense_sheet_id', 'Expense')

    def action_sheet_move_create(self):

        samples = self.mapped('expense_line_ids.sample')
        if samples.count(True):
            if samples.count(False):
                raise UserError(_("You can't mix sample expenses and regular ones"))
            self.write({'state': 'post'})
            return

        if any(sheet.state != 'approve' for sheet in self):
            raise UserError(_("You can only generate accounting entry for approved expense(s)."))

        if any(not sheet.journal_id for sheet in self):
            raise UserError(_("Specify expense journal to generate accounting entries."))

        expense_line_ids = self.mapped('expense_line_ids')\
            .filtered(lambda r: not float_is_zero(r.total_amount, precision_rounding=(r.currency_id or self.env.company.currency_id).rounding))
        res = expense_line_ids.with_context(clean_context(self.env.context)).action_move_create()

        paid_expenses_company = self.filtered(lambda m: m.payment_mode == 'company_account')
        paid_expenses_company.write({'state': 'done', 'amount_residual': 0.0, 'payment_state': 'paid'})

        paid_expenses_employee = self - paid_expenses_company
        paid_expenses_employee.write({'state': 'post'})

        self.activity_update()
        mod_request_env = self.env['mod.request'].search([('expense_sheet_id','=',self.id)])
        mod_request_env.action_complete()
        return res

    @api.depends('invoice_expense_ids.amount_total','expense_line_ids.total_amount_company')
    def _compute_amount(self):
        for sheet in self:
            monto = sheet.total_amount = sum(sheet.expense_line_ids.mapped('total_amount_company'))
            sheet.total_amount = monto+sum(sheet.invoice_expense_ids.mapped('amount_total'))

    def _get_payment_vals(self, comprobante):
        """ Hook for extension """
        payment_methods = self.bank_journal_id.outbound_payment_method_line_ids
        payment_method_id = payment_methods and payment_methods[0] or False

        return {
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'partner_id': comprobante.invoice_id.partner_id.id,
            'journal_id': self.bank_journal_id.id,
            'company_id': self.company_id.id,
            'payment_method_line_id': payment_method_id.id if payment_method_id else False,
            'amount': comprobante.amount_total,
            'currency_id': comprobante.invoice_id.currency_id.id,
            'date': self.accounting_date,
            'ref': '',
            'state': 'draft',
            'destination_account_id': comprobante.invoice_id.journal_id.account_receivable_id.id
        }

    def paid_expense(self):
        for comprobante in self.invoice_expense_ids:
            payment = self.env['account.payment'].create(self._get_payment_vals(comprobante))
            payment.action_post()

            comprobante.paid_move = payment.line_ids[0].move_id.id

            account_move_lines_to_reconcile = self.env['account.move.line']
            for line in payment.line_ids + comprobante.invoice_id.line_ids:
                if line.account_id.account_type == 'liability_payable' and not line.reconciled:
                    account_move_lines_to_reconcile |= line
                #else:
                #    line.partner_id = self.employee_id.address_home_id.id
            account_move_lines_to_reconcile.reconcile()

    
    def reset_expense_sheets(self):
        if not self.can_reset:
            raise UserError(_("Only HR Officers or the concerned employee can reset to draft."))
        self.mapped('expense_line_ids').write({'is_refused': False})
        self.sudo().write({'state': 'draft', 'approval_date': False})
        self.activity_update()
        mod_request_env = self.env['mod.request'].search([('expense_sheet_id','=',self.id)])
        mod_request_env.back_function()
        return True
    

class invoice_expense(models.Model):
    _name = 'invoice.expense'

    expense_sheet_id = fields.Many2one('hr.expense.sheet', 'Expense Sheet')
    invoice_id = fields.Many2one('account.move', 'Comprobante', required= True)
    descripcion = fields.Char('Descripción', compute='get_description')
    amount_total = fields.Float('Total en Divisa', compute='get_amount_total')
    amount_company = fields.Float('Total')
    paid_move = fields.Many2one('account.move', 'Asiento de Pago')

    analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta analitica')
    fecha = fields.Date('Fecha', compute='get_fecha')

    def get_description(self):
        for invoice_extense in self:
            if invoice_extense.invoice_id:
                invoice_extense.descripcion = invoice_extense.invoice_id.name
    
    def get_amount_total(self):
        for invoice_extense in self:
            if invoice_extense.invoice_id:
                invoice_extense.amount_total = invoice_extense.invoice_id.amount_total
    
    def get_fecha(self):
        for invoice_extense in self:
            if invoice_extense.invoice_id:
                invoice_extense.fecha = invoice_extense.invoice_id.invoice_date

    @api.onchange('invoice_id')
    def onchange_invoice_id(self):

        for invoice_extense in self:
            factura = invoice_extense.invoice_id

            descripcion = factura.name
            amount_total = factura.amount_total
            amount_company = factura.amount_total_signed*-1

            fecha = factura.invoice_date
            
            invoice_extense.write({
                                    'descripcion': descripcion,
                                    'amount_total': amount_total,
                                    'amount_company': amount_company,
                                    'fecha': fecha
                                    })
