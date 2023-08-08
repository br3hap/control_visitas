# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class account_move(models.Model):
    _inherit = 'account.move'

    @api.depends('name','partner_id','enable_whatsapp')
    def _enable_whatsapp(self):
        is_enable = self.env['ir.config_parameter'].sudo().get_param('whatsapp.whatsapp_enable', default=False)
        is_enable_invoice = self.env['ir.config_parameter'].sudo().get_param('whatsapp_invoice.whatsapp_enable_invoice', default=False)
        for wsp in self:
            if wsp and is_enable and is_enable_invoice:
                wsp.enable_whatsapp = True
            else:
                wsp.enable_whatsapp = False

    enable_whatsapp = fields.Boolean(compute='_enable_whatsapp', string='enable whatsapp')

    def whatsapp_send_invoice(self):
        url = self.env['ir.config_parameter'].sudo().get_param('whatsapp.whatsapp_enable', default=False)
        if not url:
            return
        if not self.partner_id.mobile:
            raise UserError(_('first enter the partner mobile number.'))
        if not self.invoice_line_ids:
            raise UserError(_('The order has no products.'))

        message_body = self.whatsapp_message_body()
        message_view = self.whatsapp_message_view('\n')
        message_history = self.whatsapp_message_view('<br>')
        invoice = 'Borrador'
        if self.name and self.name!="/":
            invoice = 'Nº ' + self.name
        affair = _('Invoice %s') %(invoice)
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': 
                    {
                        'default_user_id': self.partner_id.id,
                        'default_affair': affair,
                        'default_message': message_body,
                        'default_message_wsp': message_view,
                        'default_message_history': message_history,
                        'default_show_note':True,
                        'default_res_id': str(self.id),
                        'default_object_origin': 'account.move',
                    },
                }

    def whatsapp_message_body(self):
        linefeed = '%0A'
        tab = '%09'
        response = '*' + self.company_id.display_name+ '*' + linefeed +'\n'
        if self.company_id.email:
            response += self.company_id.email + linefeed+linefeed +'\n\n'
        else:
            response += linefeed+'\n'
        name_partner = ''
        if self.partner_id.name:
            name_partner += self.partner_id.name
        elif self.partner_id.name:
            name_partner += self.partner_id.name
        response += _('Hello *%s* %s\n\n') % (name_partner,linefeed)
        invoice = 'borrador'
        if self.name and self.name!="/":
            invoice = self.name
        response += _('Your invoice *%s* %s%s\n') %(invoice,linefeed,linefeed)
        response += _('*DETAIL* %s\n') % (linefeed)
        for line in self.invoice_line_ids:
            product_name = line.product_id.name if line.product_id.name else line.name
            response += _('*%s*%s\n') % (product_name,linefeed)
            response += _('_Cant:_  %s%s_P.unit:_ %s%s%s_Total:_ %s%s%s\n') % (str(line.quantity),tab,self.currency_id.symbol,str((float("{:.2f}".format(line.price_unit)))),tab,self.currency_id.symbol,(float("{:.2f}".format(line.price_total))),linefeed)
        response += linefeed +'\n'
        response += _('Amount: %s*%s %s* %s\n') % (tab,self.currency_id.symbol,self.amount_untaxed,linefeed)
        response += _('Tax: %s*%s %s* %s\n') % (tab,self.currency_id.symbol,self.amount_tax,linefeed)
        response += '----------------------------------' + linefeed + '\n'
        response += _('Amount Total: %s*%s %s*') % (tab,self.currency_id.symbol,self.amount_total)
        return response

    def whatsapp_message_view(self,linefeed):
        response = self.company_id.display_name + linefeed
        if self.company_id.email:
            response += self.company_id.email + linefeed + linefeed
        else:
            response += linefeed
        name_partner = ''
        if self.partner_id.name:
            name_partner += self.partner_id.name
        elif self.partner_id.name:
            name_partner += self.partner_id.name
        response += _('Hello, %s%s%s') % (name_partner,linefeed,linefeed)
        invoice = 'borrador'
        if self.name and self.name!="/":
            invoice = self.name
        response += _('Your invoice %s%s') %(invoice,linefeed)
        response += _('DETAIL%s') %(linefeed)
        for line in self.invoice_line_ids:
            product_name = line.product_id.name if line.product_id.name else line.name
            response += _('%s%s') % (product_name,linefeed)
            response += _('Cant:%s  P.unit:%s%s  Total:%s%s%s') % (str(line.quantity),self.currency_id.symbol,str((float("{:.2f}".format(line.price_unit)))),self.currency_id.symbol,(float("{:.2f}".format(line.price_total))),linefeed)
        response += linefeed
        response += _('Amount: %s %s %s') % (self.currency_id.symbol,self.amount_untaxed,linefeed)
        response += _('Tax: %s %s %s') % (self.currency_id.symbol,self.amount_tax,linefeed)
        response += '----------------------------------' + linefeed
        response += _('Amount Total: %s %s') % (self.currency_id.symbol,self.amount_total)
        return response

    def messagge_email_data(self,body):
        MailMessage_sudo = self.env['mail.message'].sudo()
        parent_message = MailMessage_sudo.search([('res_id', '=', self.id), ('model', '=', 'account.move'), ('message_type', '!=', 'user_notification')], order="id ASC", limit=1)
        # email_data = self._message_compute_author(None, None, raise_exception=True)
        subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')
        values_list = []
        values = {}
        # values['author_id'] = email_data['author_id']  
        # values['email_from'] =email_data['email_from'] 
        values['model']='account.move'
        values['res_id']=self.id
        values['body']=body
        values['subject']=False
        values['message_type']='comment'
        values['parent_id']=parent_message.id
        values['subtype_id']=subtype_id
        values['partner_ids']=[]
        # values['channel_ids']=[]
        # values['add_sign']=True
        values['record_name']=self.name
        values_list.append(values)
        return values_list