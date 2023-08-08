# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class product_category(models.Model):
    _inherit="product.category"
    
    adjustment_valuation_account = fields.Many2one('account.account', 'Adjustment valuation account')
    missing_expense_account = fields.Many2one('account.account', 'Missing expense account')
    surplus_expense_account = fields.Many2one('account.account', 'Surplus expense account')
    
    
    
    
    
    
    