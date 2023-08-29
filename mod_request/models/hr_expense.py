# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero
from datetime import date
from datetime import datetime
from odoo.tools.misc import clean_context, format_date
import logging
_logger = logging.getLogger(__name__) 

class hr_expense_inherit(models.Model):

    _inherit = 'hr.expense'


    people_id = fields.Many2one('res.partner')
    description_rq = fields.Char(string='Descripcion')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica')


    def _convert_to_tax_base_line_dict(self, base_line=None, currency=None, price_unit=None, quantity=None):
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            base_line,
            currency=currency or self.currency_id,
            product=self.product_id,
            taxes=self.tax_ids,
            price_unit=price_unit or self.total_amount_company,
            quantity=quantity or 1,
            account=self.account_id,
            analytic_distribution=self.analytic_distribution,
            extra_context={'force_price_include': True},
        )




class hr_expense_sheet_inherit(models.Model):
    _inherit = 'hr.expense.sheet'



    def _prepare_payment_vals(self):
        self.ensure_one()
        payment_method_line = self.env['account.payment.method.line'].search(
            [('payment_type', '=', 'outbound'),
             ('journal_id', '=', self.bank_journal_id.id),
             ('code', '=', 'manual'),
             ('company_id', '=', self.company_id.id)], limit=1)
        if not payment_method_line:
            raise UserError(_("You need to add a manual payment method on the journal (%s)", self.bank_journal_id.name))

        if not self.expense_line_ids or self.is_multiple_currency:
            currency = self.company_id.currency_id
            amount = self.total_amount
        else:
            currency = self.expense_line_ids[0].currency_id
            amount = sum(self.expense_line_ids.mapped('total_amount'))
        rate = amount / self.total_amount if self.total_amount else 0.0
        move_lines = []
        for expense in self.expense_line_ids:
            # Due to rounding and conversion mismatch between vendor bills and payments, we have to force the computation into company account
            amount_currency_diff = expense.total_amount_company if currency == expense.company_currency_id else expense.total_amount
            last_expense_line = None # Used for rounding in currency issues
            tax_data = self.env['account.tax']._compute_taxes([expense._convert_to_tax_base_line_dict()])
            for base_line_data, update in tax_data['base_lines_to_update']:  # Add base lines
                base_line_data.update(update)
                amount_currency = currency.round(base_line_data['price_subtotal'] * rate)
                expense_name = expense.name.split("\n")[0][:64]
                last_expense_line = base_move_line = {
                    'name': f'{expense.employee_id.name}: {expense_name}',
                    'account_id':base_line_data['account'].id,
                    'product_id': base_line_data['product'].id,
                    'analytic_distribution': base_line_data['analytic_distribution'],
                    'expense_id': expense.id,
                    'tax_ids': [Command.set(expense.tax_ids.ids)],
                    'tax_tag_ids': base_line_data['tax_tag_ids'],
                    'balance': base_line_data['price_subtotal'],
                    'amount_currency': amount_currency,
                    'currency_id': currency.id,
                    'partner_id':expense.people_id.id
                }
                amount_currency_diff -= amount_currency
                move_lines.append(base_move_line)
            for tax_line_data in tax_data['tax_lines_to_add']:  # Add tax lines
                amount_currency = currency.round(tax_line_data['tax_amount'] * rate)
                last_expense_line = tax_line = {
                    'name': self.env['account.tax'].browse(tax_line_data['tax_id']).name,
                    'display_type': 'tax',
                    'account_id': tax_line_data['account_id'],
                    'analytic_distribution': tax_line_data['analytic_distribution'],
                    'expense_id': expense.id,
                    'tax_tag_ids': tax_line_data['tax_tag_ids'],
                    'balance': tax_line_data['tax_amount'],
                    'amount_currency': amount_currency,
                    'currency_id': currency.id,
                    'tax_repartition_line_id': tax_line_data['tax_repartition_line_id'],
                }
                move_lines.append(tax_line)
                amount_currency_diff -= amount_currency
            if not currency.is_zero(amount_currency_diff) and last_expense_line:
                last_expense_line['amount_currency'] += amount_currency_diff
        expense_name = self.name.split("\n")[0][:64]
        move_lines.append({  # Add outstanding payment line
            'name': f'{self.employee_id.name}: {expense_name}',
            'display_type': 'payment_term',
            'account_id': self.expense_line_ids[0]._get_expense_account_destination(),
            'balance': -self.total_amount,
            'amount_currency': currency.round(-amount),
            'currency_id': currency.id,
            # 'partner_id':self.employee_id.address_home_id.id
            'partner_id':expense.employee_id.address_home_id.id
        })
        _logger.warning('move_lines', move_lines)
        return {
            **self._prepare_move_vals(),
            'journal_id': self.bank_journal_id.id,
            'move_type': 'entry',
            'amount': amount,
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'payment_method_line_id': payment_method_line.id,
            'currency_id': currency.id,
            'line_ids': [Command.create(line) for line in move_lines],
        }
