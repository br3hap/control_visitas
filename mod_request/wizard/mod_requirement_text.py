# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class mod_request_json_text(models.TransientModel):
    _name = 'mod.requirement.text.wizard'

    text = fields.Text(string = 'Text Json')

    def default_get(self, fields):
        c = super(mod_request_json_text, self).default_get(fields)
        text = self._context['get_json_text']
        c['text'] = text
        return c
	
	