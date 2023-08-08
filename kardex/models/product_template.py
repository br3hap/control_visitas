# -*- coding: utf-8 -*-
from odoo import fields, models


class product_template(models.Model):
    _inherit="product.template"
    
    type_existence = fields.Many2one('peb.catalogue.05', string='Type of existence')
    
    """
    Validar que tanto impacta realizar esta asociación con los stocks inicales por periodo del kardex, ya que 
    al menos se tendrá por cada mes de uso del sistema, una cantidad de registros asociados igual a la cantidad 
    de almacenes de la empresa (siempre y cuando el producto se encuentre en ese almacén)
    """
    #product_kardex_id = fields.One2many('stock.init.kardex', 'product_id', string='Initial stock per warehouse')
    
