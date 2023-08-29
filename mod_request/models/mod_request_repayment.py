# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero
from datetime import date
from datetime import datetime
from odoo.tools.misc import clean_context, format_date
import logging
_logger = logging.getLogger(__name__) 

class mod_request_repayment(models.Model):

    _name = 'mod.request.repayment'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'analytic.mixin']
    _description = _("Repayment")

    _order = 'create_date desc'


    name = fields.Char('Name')
    for_liquidation = fields.Boolean(string='Con Liquidacion')