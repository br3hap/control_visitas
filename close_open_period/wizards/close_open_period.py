from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import ValidationError


class CloseOpenPeriod(models.TransientModel):

    _name = "close.open.period"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    
    period_ini = fields.Many2one('account.period', 'Periodo', required=True)

    def open(self):
        for rec in self:
            if rec.period_ini.state == 'close':
                rec.period_ini.write({'state': 'open'})

    def close(self):
        for rec in self:
            if rec.period_ini.state == 'open':
                rec.period_ini.write({'state': 'close'})
