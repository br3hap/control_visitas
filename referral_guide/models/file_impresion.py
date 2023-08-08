# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class impresiones(models.TransientModel):
    _name='impresion'
    
    file_id = fields.Binary('Impresion Temporal')