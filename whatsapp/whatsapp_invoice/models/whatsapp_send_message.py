# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class whatsapp_send_message(models.TransientModel):

    _inherit = 'whatsapp.message.wizard'

    def history_invoice(self):
        sale_order = self.env['account.move'].search([('id','=',int(self.res_id))],limit=1)
        body = _('<strong>Sending By WhatsApp:</strong><br>')
        if self.affair:
            body += _('affair: %s%s') % (self.affair,'<br>')
        if self.message_history:
            body += self.message_history
        if self.note:
            body += _('<br><br>Note: %s') % (self.note)
        values_list = sale_order.messagge_email_data(body)
        self.env['mail.message'].create(values_list)
        response = super(whatsapp_send_message, self).history_invoice()