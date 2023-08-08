from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, UserError

class account_move(models.Model):
    _inherit = 'account.move'

    pago_credito = fields.Boolean('Pago al Crédito')
    cuotas = fields.One2many('cuotas', 'move_id', 'Cuotas')


class cuotas(models.Model):
    _name = 'cuotas'
    _description = 'cuotas'
    name = fields.Char('Nombre', required=True, default='Cuota001')
    amount = fields.Float('Monto de la cuota', required=True)
    date = fields.Date('Fecha de Vencimiento', required=True)
    move_id = fields.Many2one('account.move', 'Comprobante', required=True)