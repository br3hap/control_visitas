# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests
from odoo.http import request
from odoo.exceptions import UserError
import base64
from datetime import datetime, date
import logging
_logger = logging.getLogger(__name__)   

class mod_request_inherit(models.Model):
    _inherit = 'mod.request'
    _description = _("Requirements and Request")

    def button_function(self):
        _logger.warning('Presionaste el boton')
