# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    Authonr Salcedo Salazar Juan Diego salcedo.salazar@gmail.com
#
##############################################################################

#from openerp import models, fields, api, _
from odoo import models, fields, api, _

class logs_guia_remision(models.Model):
    _name = 'logs.guia.remision'
    _order = 'fecha,id'

    guia_remision_id = fields.Many2one('stock.picking', readonly=True)
    fecha = fields.Datetime(string='Fecha')
    descripcion = fields.Char('Descripción')
    estado_ini = fields.Char('Estado Inicial')
    estado_fin = fields.Char('Estado Final')
    descripcion_detallada = fields.Text("Descripción Detallada")