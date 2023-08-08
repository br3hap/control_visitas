# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import except_orm

class account_move(models.Model):
    _inherit = "account.move"

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:

            journal = self.journal_id
            value_dic = dict(currency_id=journal.currency_id.id or journal.company_id.currency_id.id,
                             company_id=journal.company_id.id)

            if self.line_ids and self.line_ids.account_id:
                for line in self.line_ids:
                    if line.account_id:
                        if line.account_id.account_type in ('asset_receivable','liability_payable') and self.journal_id.account_receivable_id:
                            line.account_id = self.journal_id.account_receivable_id.id
                        

                    
            return dict(value=value_dic)

class account_move_line(models.Model):
    _inherit = "account.move.line"
    _name =  "account.move.line"

    @api.depends('display_type', 'company_id')
    def _compute_account_id(self):
        super()._compute_account_id()
        for line in self:
            if line:
                if line.move_id.journal_id and line.move_id.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund'):

                    journal = line.move_id.journal_id

                    if line.account_id:
                        if line.account_id.account_type in ('asset_receivable','liability_payable') and journal.account_receivable_id:
                            line.account_id = journal.account_receivable_id.id

        return self