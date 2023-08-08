from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    _sql_constraints = [('api_code_unique', 'unique(api_code)','a journal already exists with this api code')]

    api_code =  fields.Char(string='API code')

    