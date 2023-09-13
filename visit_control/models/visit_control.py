
from odoo import models, fields, api, _
import requests
from odoo.http import request
from odoo.exceptions import UserError
import base64
from datetime import datetime, date
import logging
_logger = logging.getLogger(__name__)   

class visit_control(models.Model):
    _name = 'visit.control'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = _("Visit Control")

    _order = 'create_date desc'


    name = fields.Char(string='Codigo', required=True, copy=False, default='New')
    date = fields.Datetime(string='Date and Time', required=True)
    name_visit = fields.Char(string='Visitor name', required=True)
    patient_id = fields.Many2one('res.partner', string='Patient', required=True)
    description = fields.Text(string='Reason for visit', required=True)


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('visit.control') or 'New'
        result = super(visit_control, self).create(vals)
        return result
 