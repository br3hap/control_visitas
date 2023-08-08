# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class whatsapp_send_message(models.TransientModel):

    _name = 'whatsapp.message.wizard'

    user_id = fields.Many2one('res.partner', string="Recipient", readonly=True)
    mobile = fields.Char(related='user_id.mobile', required=True)
    affair = fields.Text(string="affair")
    message = fields.Text(string="message", required=True)
    message_wsp = fields.Text(string="message",default=False, readonly=True)
    message_history = fields.Text(string="message",default=False, readonly=True)
    note = fields.Text(string="note",default=False)
    show_note = fields.Boolean(default=False)
    res_id = fields.Char()
    object_origin = fields.Char()

    def send_message(self):
        if self.object_origin == 'res.partner':
            self.history_partner()
        elif self.object_origin == 'account.move':
            self.history_invoice()
        elif self.object_origin == 'sale.order':
            self.history_sale()
        elif self.object_origin == 'crm.lead':
            self.history_crm()
            
        message_send = ''
        note_send = ''
        if self.affair:
            message_send += _('*affair:* *%s*%s') % (self.affair,'%0A%0A')
        if self.message:
            message_send += self.message
        if self.message_wsp:
            note_send = _('*note:* ')
        if self.note:
            message_send += '%0A%0A'+ note_send + self.note

        if message_send and self.mobile:
            message_string = ''
            message = message_send.split(' ')
            for msg in message:
                message_string = message_string + msg + '%20'
            message_string = message_string[:(len(message_string) - 3)]
            url = self.env['ir.config_parameter'].sudo().get_param('whatsapp.whatsapp_api_url', default=False)
            message_string = self.validate_spacial_character(message_string)
            return {
                'type': 'ir.actions.act_url',
                'url': url + self.user_id.mobile+"&text=" + message_string,
                'target': 'new',
                'res_id': self.id,
            }
            # https://api.whatsapp.com/send?phone=
    
    def validate_spacial_character(self, msg_str):
        """
        Verifica el envio de caracteres especiales para evitar que se corte el mensaje.
        @Autor: MRamirez
        @params str msg_str: cadena a ser evaluado.
        @return str msg_str: cadena quitando y reemplazndo los caracteres especiales
        """
        character_spaecials = [{'character':'&','value':'%26'},{'character':'#', 'value':'%23'}]
        for character in character_spaecials:
            msg_str = msg_str.replace(character['character'], character['value'])
        return msg_str

    # funciones que seran Heredadas por  modulos dependientes para insertar un historial
    def history_partner(self):
        res_partner = self.env['res.partner'].search([('id','=',int(self.res_id))],limit=1)
        body = _('<strong>Sending By WhatsApp:</strong><br>')
        if self.affair:
            body += _('affair: %s%s') % (self.affair,'<br>')
        if self.message:
            body += self.message
            
        values_list = res_partner.messagge_email_data(body)
        self.env['mail.message'].create(values_list)

    def history_invoice(self):
        return 
    def history_sale(self):
        return
    def history_crm(self):
        return

