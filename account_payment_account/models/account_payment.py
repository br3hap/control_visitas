# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HrExpense(models.Model):
    _name = "hr.expense"
    _inherit = "hr.expense"

    def _get_expense_account_destination(self):
        self.ensure_one()
        account_dest = self.env['account.account']
        if self.payment_mode == 'company_account':
            journal = self.sheet_id.bank_journal_id
            account_dest = (
                journal.outbound_payment_method_line_ids[0].payment_account_id
                or journal.default_account_id
            )
        else:
            if not self.employee_id.sudo().address_home_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (self.employee_id.name))
            partner = self.employee_id.sudo().address_home_id.with_company(self.company_id)
            account_dest = partner.property_account_payable_id or partner.parent_id.property_account_payable_id
        return account_dest.id

class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'

    @api.depends('journal_id', 'payment_type', 'payment_method_line_id')
    def _compute_outstanding_account_id(self):
        for pay in self:
            if pay.payment_type == 'inbound':
                pay.outstanding_account_id = (pay.payment_method_line_id.payment_account_id
                                              or pay.journal_id.default_account_id)
            elif pay.payment_type == 'outbound':
                pay.outstanding_account_id = (pay.payment_method_line_id.payment_account_id
                                              or pay.journal_id.default_account_id)
            else:
                pay.outstanding_account_id = False
    

    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer', 'destination_journal_id')
    def _compute_destination_account_id(self):
        if not self.destination_account_id:
            self.destination_account_id = False
            for pay in self:
                if pay.is_internal_transfer:
                    pay.destination_account_id = pay.destination_journal_id.company_id.transfer_account_id
                elif pay.partner_type == 'customer':
                    # Receive money from invoice or send money to refund it.
                    if pay.partner_id:
                        pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_receivable_id
                    else:
                        pay.destination_account_id = self.env['account.account'].search([
                            ('company_id', '=', pay.company_id.id),
                            ('account_type', '=', 'asset_receivable'),
                            ('deprecated', '=', False),
                        ], limit=1)
                elif pay.partner_type == 'supplier':
                    # Send money to pay a bill or receive money to refund it.
                    if pay.partner_id:
                        pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_payable_id
                    else:
                        pay.destination_account_id = self.env['account.account'].search([
                            ('company_id', '=', pay.company_id.id),
                            ('account_type', '=', 'liability_payable'),
                            ('deprecated', '=', False),
                        ], limit=1)
    
    def _synchronize_from_moves(self, changed_fields):
        ''' Update the account.payment regarding its related account.move.
        Also, check both models are still consistent.
        :param changed_fields: A set containing all modified fields on account.move.
        '''

        return 
        
        if self._context.get('skip_account_move_synchronization'):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):

            # After the migration to 14.0, the journal entry could be shared between the account.payment and the
            # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
            if pay.move_id.statement_line_id:
                continue

            move = pay.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}

            if 'journal_id' in changed_fields:
                if pay.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))

            if 'line_ids' in changed_fields:
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                #if len(liquidity_lines) != 1:
                #    raise UserError(_(
                #        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                #        "include one and only one outstanding payments/receipts account.",
                #        move.display_name,
                #    ))

                #if len(counterpart_lines) != 1:
                #    raise UserError(_(
                #        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                #        "include one and only one receivable/payable account (with an exception of "
                #        "internal transfers).",
                #        move.display_name,
                #    ))

                if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "share the same currency.",
                        move.display_name,
                    ))

                if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "share the same partner.",
                        move.display_name,
                    ))

                if counterpart_lines.account_id.account_type == 'asset_receivable':
                    partner_type = 'customer'
                else:
                    partner_type = 'supplier'

                liquidity_amount = liquidity_lines.amount_currency

                move_vals_to_write.update({
                    'currency_id': liquidity_lines.currency_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                payment_vals_to_write.update({
                    'amount': abs(liquidity_amount),
                    'partner_type': partner_type,
                    'currency_id': liquidity_lines.currency_id.id,
                    'destination_account_id': counterpart_lines.account_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                if liquidity_amount > 0.0:
                    payment_vals_to_write.update({'payment_type': 'inbound'})
                elif liquidity_amount < 0.0:
                    payment_vals_to_write.update({'payment_type': 'outbound'})

            #move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
            #pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))