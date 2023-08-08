# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class pos_order(models.Model):
    _inherit = 'pos.order'

    @api.depends('name','partner_id','enable_whatsapp')
    def _enable_whatsapp(self):
        is_enable = self.env['ir.config_parameter'].sudo().get_param('whatsapp.whatsapp_enable', default=False)
        is_enable_order = self.env['ir.config_parameter'].sudo().get_param('whatsapp_order.whatsapp_enable_order', default=False)
        for wsp in self:
            if wsp and is_enable and is_enable_order:
                wsp.enable_whatsapp = True
            else:
                wsp.enable_whatsapp = False

    enable_whatsapp = fields.Boolean(compute='_enable_whatsapp', string='enable whatsapp')

    def whatsapp_send_order(self):
        url = self.env['ir.config_parameter'].sudo().get_param('whatsapp.whatsapp_enable', default=False)
        if not url:
            return
        if not self.partner_id.mobile:
            raise UserError(_('first enter the partner mobile number.'))
        if not self.lines:
            raise UserError(_('The order has no products.'))

        message_body = self.whatsapp_message_body()
        message_view = self.whatsapp_message_view('\n')
        affair = _('Order %s') %(self.name)
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
                        'default_show_note':True,
                        'default_res_id': str(self.id),
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
        response += _('Your order *%s* %s%s\n') %(self.name,linefeed,linefeed)
        response += _('*DETAIL* %s\n') % (linefeed)
        for line in self.lines:
            product_name = line.product_id.name if line.product_id.name else line.display_name
            response += _('*%s*%s\n') % (product_name,linefeed)
            response += _('_Cant:_  %s%s_P.unit:_ %s%s%s_Total:_ %s%s%s\n') % (str(line.qty),tab,self.currency_id.symbol,str((float("{:.2f}".format(line.price_unit)))),tab,self.currency_id.symbol,(float("{:.2f}".format(line.price_subtotal_incl))),linefeed)
        response += linefeed +'\n'
        amount_untaxed = self.amount_total- self.amount_tax
        response += _('Amount: %s*%s %s* %s\n') % (tab,self.currency_id.symbol,float("{:.2f}".format(amount_untaxed)),linefeed)
        response += _('Tax: %s*%s %s* %s\n') % (tab,self.currency_id.symbol,self.amount_tax,linefeed)
        response += '----------------------------------' + linefeed + '\n'
        response += _('Amount Total: %s*%s %s*') % (tab,self.currency_id.symbol,self.amount_total)
        return response

    def whatsapp_message_view(self,linefeed):
        response = self.company_id.display_name+ linefeed
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
        response += _('Your order %s%s') %(self.name,linefeed)
        response += _('DETAIL%s') % (linefeed)
        for line in self.lines:
            product_name = line.product_id.name if line.product_id.name else line.display_name
            response += _('%s%s') % (product_name,linefeed)
            response += _('Cant:%s  P.unit:%s%s  Total:%s%s%s') % (str(line.qty),self.currency_id.symbol,str((float("{:.2f}".format(line.price_unit)))),self.currency_id.symbol,(float("{:.2f}".format(line.price_subtotal_incl))),linefeed)
        response += linefeed
        amount_untaxed = self.amount_total- self.amount_tax
        response += _('Amount: %s %s %s') % (self.currency_id.symbol,float("{:.2f}".format(amount_untaxed)),linefeed)
        response += _('Tax: %s %s %s') % (self.currency_id.symbol,self.amount_tax,linefeed)
        response += '----------------------------------' + linefeed
        response += _('Amount Total: %s %s') % (self.currency_id.symbol,self.amount_total)
        return response
