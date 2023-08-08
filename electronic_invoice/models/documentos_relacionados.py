# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class documentos_relacionados(models.Model):
    _name = "documento.relacionados"
    _description = 'documento.relacionados'
    documentos = fields.Many2one('account.move', 'Tipo de Documento')
    tipo = fields.Many2one("peb.catalogue.01", string="Tipo de Documento", required=True)
    serie = fields.Char('Serie', required=True)
    correlativo = fields.Char('Correlativo', required=True)

    # Autor: Denis Ernesto Ninaco Cerón
    @api.constrains('serie')
    def constrain_serie(self):
            if len(self.serie) != 4:
                raise ValidationError(("La Serie debe contener 4 digitos."))

    # Autor: Denis Ernesto Ninaco Cerón
    @api.constrains('correlativo')
    def constrain_correlativo(self):
            if len(self.correlativo) > 8:
                raise ValidationError(("El Correlativo debe contener como maximo 8 digitos."))
                    

class accoount_move(models.Model):
    _inherit = "account.move"
    
    documentos = fields.One2many('documento.relacionados', 'documentos', 'Tipo de Documento')
