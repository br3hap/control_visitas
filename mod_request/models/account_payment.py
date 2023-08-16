# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero
from datetime import date
from datetime import datetime
from odoo.tools.misc import clean_context, format_date
import logging
_logger = logging.getLogger(__name__) 

class account_payment_inherit(models.Model):
    _inherit='account.payment'

    lines_req = fields.One2many('account.payment.lines.req', 'account_id')


class account_payment_lines_req(models.Model):
    _name = 'account.payment.lines.req'

    account_id = fields.Many2one('account.payment', ondelete='cascade')
    cod_requirement = fields.Char('Cod. Requirement')
    amount_requirement = fields.Float('Amount')