# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import uuid
import requests
class OdooRestApi(models.Model):
    _name = 'odoo.rest.api'

    name = fields.Char(string='Name')
    account_token = fields.Char(default=lambda s: uuid.uuid4().hex)
    customer_ids = fields.One2many('customer.rest.api', 'odoo_api_id', string='Customer')
   

