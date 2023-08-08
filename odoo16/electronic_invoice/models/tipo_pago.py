from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, UserError

class tipo_pago(models.Model):
    _name='tipo.pago'
    _description = 'tipo.pago'
    code = fields.Char("Código", required=True)
    description = fields.Char("Descripción", required=True)
    
    @api.depends('code', 'description')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name +=  table.description
            result.append((table.id, l_name ))
        return result