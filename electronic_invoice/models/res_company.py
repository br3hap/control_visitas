# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_company(models.Model):
    _inherit = 'res.company'

    pass_security = fields.Char('Password Security')
    emisor_code = fields.Char('Emisor Code')

   