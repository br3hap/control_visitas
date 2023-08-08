# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class whatsapp_send_message(models.TransientModel):

    _inherit = 'whatsapp.message.wizard'

    def history_crm(self):
        res_partner = self.env['crm.lead'].search([('id','=',int(self.res_id))],limit=1)
        body = _('<strong>Sending By WhatsApp:</strong><br>')
        if self.affair:
            body += _('affair: %s%s') % (self.affair,'<br>')
        if self.message:
            body += self.message
            
        values_list = res_partner.messagge_email_data(body)
        self.env['mail.message'].create(values_list)