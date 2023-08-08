from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class SettingsExpensesInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_shortening_processes = fields.Boolean(string='Allow shortening processes in the creation of spending')
    account_expenses_pen = fields.Many2one('account.account', 'Account Expenses PEN', config_parameter="mod_request.account_expenses_pen")
    account_expenses_usd = fields.Many2one('account.account', 'Account Expenses USD', config_parameter="mod_request.account_expenses_usd")


    def set_values(self):
        res = super(SettingsExpensesInherit, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('mod_request.allow_shortening_processes', self.allow_shortening_processes)
        # self.env['ir.config_parameter'].sudo().set_param('mod_request.account_expenses_pen', self.account_expenses_pen)
        # self.env['ir.config_parameter'].sudo().set_param('mod_request.account_expenses_usd', self.account_expenses_usd)
        return res

    @api.model
    def get_values(self):
        res = super(SettingsExpensesInherit, self).get_values()
        allow_shortening_processes = bool(self.env['ir.config_parameter'].sudo().get_param('mod_request.allow_shortening_processes'))
        # account_expenses_pen = self.env['ir.config_parameter'].sudo().get_param('mod_request.account_expenses_pen')
        # account_expenses_usd = self.env['ir.config_parameter'].sudo().get_param('mod_request.account_expenses_usd')
        # _logger.warning("account_expenses_pen", account_expenses_pen, account_expenses_usd)

        res.update({
            'allow_shortening_processes' : allow_shortening_processes,
            # 'account_expenses_pen' : account_expenses_pen,
            # 'account_expenses_usd' : account_expenses_usd,
            })
        return res
