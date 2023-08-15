# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class mod_request_report_date(models.TransientModel):
    _name = 'mod.request.report.date.wizard'

    date_from =   fields.Date('Fecha Inicio', required=True)
    date_to   =   fields.Date('Fecha fin', required=True)
	