from odoo import _, models, fields, api
from odoo.exceptions import ValidationError, except_orm


class AccountMove(models.Model):
    _inherit = "account.move"

    def validar_period(self):
        if self.period_id:
            if self.period_id.state == 'close':
                raise ValidationError(_("You cannot perform operations for closed periods"))

    def action_post(self):
        self.validar_period()
        return super().action_post()

    def button_cancel(self):
        self.validar_period()
        return super().button_cancel()

    def button_draft(self):
        self.validar_period()
        return super().button_draft()
    
    def post(self):
        self.validar_period()
        return super().post()
    
    # write, unlink, create

    def write(self,vals):
        self.validar_period()
        return super(AccountMove, self).write(vals)
    
    # @api.model
    # def create(self,vals):
    #     if 'invoice_date' in vals.keys() or 'date' in vals.keys():
    #         # if 'period_id' in vals.keys():
    #         period = self.env['account.period']
    #         if 'invoice_date' in vals.keys() and (vals['invoice_date'] is not False):
    #             period_obj = period.search([('date_start', '<=',vals['invoice_date']),
    #                                     ('date_stop', '>=',vals['invoice_date'])],limit=1)
    #         else: # Cuando se crea pagos se utiliza date
    #             period_obj = period.search([('date_start', '<=',vals['date']),
    #                                     ('date_stop', '>=',vals['date'])],limit=1)
    #         if period_obj:
    #             if period_obj.state == 'close':
    #                 raise ValidationError(_("You cannot perform operations for closed periods"))
        
    #     return super(AccountMove, self).create(vals)

