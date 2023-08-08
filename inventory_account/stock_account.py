# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_is_zero

import logging
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_accounting_data_for_valuation(self):
        """ Return the accounts and journal to use to post Journal Entries for
        the real-time valuation of the quant. """
        self.ensure_one()
        self = self.with_context(force_company=self.company_id.id)
        accounts_data = self.product_id.product_tmpl_id.get_product_accounts()

        if self.location_id.valuation_out_account_id:
            acc_src = self.location_id.valuation_out_account_id.id
        else:
            acc_src = accounts_data['stock_input'].id

        if self.location_dest_id.valuation_in_account_id:
            acc_dest = self.location_dest_id.valuation_in_account_id.id
        else:
            acc_dest = accounts_data['stock_output'].id

        acc_valuation = accounts_data.get('stock_valuation', False)
        if acc_valuation:
            acc_valuation = acc_valuation.id
        if not accounts_data.get('stock_journal', False):
            raise UserError(_('You don\'t have any stock journal defined on your product category, check if you have installed a chart of accounts.'))
        if not acc_src:
            raise UserError(_('Cannot find a stock input account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.display_name))
        if not acc_dest:
            raise UserError(_('Cannot find a stock output account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.display_name))
        if not acc_valuation:
            raise UserError(_('You don\'t have any stock valuation account defined on your product category. You must define one before processing this operation.'))
        journal_id = accounts_data['stock_journal'].id


        # DNINACO CAMBIO PARA LA CONTABILIDAD DE AJUSTES DE INVENTARIO
        if self.location_id.usage == 'inventory' or self.location_dest_id.usage == 'inventory':
            missing_expense_account = self.product_id.product_tmpl_id.categ_id.missing_expense_account
            surplus_expense_account = self.product_id.product_tmpl_id.categ_id.surplus_expense_account
            account_valuation = self.product_id.product_tmpl_id.categ_id.adjustment_valuation_account
            if not missing_expense_account:
                raise UserError(_('Expense account was not assigned for missing inventory'))
            if not surplus_expense_account:
                raise UserError(_('No expense account was assigned for surplus inventory'))
            if not account_valuation:
                raise UserError(_('No valuation account was assigned for inventory adjustment'))

            acc_dest = missing_expense_account.id
            acc_src = surplus_expense_account.id
            acc_valuation = account_valuation.id
        #

        return journal_id, acc_src, acc_dest, acc_valuation