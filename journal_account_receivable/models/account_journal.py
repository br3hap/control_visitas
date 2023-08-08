# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class account_journal(models.Model):

    _inherit = "account.journal"

    account_receivable_id = fields.Many2one('account.account', company_dependent=True,
                                string="Cuenta por cobrar",
                                domain="[('account_type', 'in', ['asset_receivable','liability_payable']), ('deprecated', '=', False)]",
                                help="This account will be used instead of the default one as the receivable account for the current partner")