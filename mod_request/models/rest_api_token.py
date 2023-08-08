# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import uuid

class RestApiToken(models.Model):
    _name = 'rest.api.token'
    _description = _("Rest Api Token")


    _sql_constraints = [('name_unique', 'unique(name)','name already exists')]

    name = fields.Char(string='Name')
    account_token = fields.Char(default=lambda s: uuid.uuid4().hex)


class RestApiUrl(models.Model):
    _name = 'rest.api.url'
    _description = _("Rest Api Url")

    _sql_constraints = [('name_unique', 'unique(name)','name already exists')]

    name = fields.Char(string="Name")
    url = fields.Char(string="Url")

