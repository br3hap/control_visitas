# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.depends('name','partner_id','enable_whatsapp')
    def _enable_whatsapp(self):
        is_enable = self.env['ir.config_parameter'].sudo().get_param('whatsapp.whatsapp_enable', default=False)
        is_enable_sale = self.env['ir.config_parameter'].sudo().get_param('whatsapp_sale.whatsapp_enable_sale', default=False)
        for wsp in self:
            if wsp and is_enable and is_enable_sale:
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
        if not self.order_line:
            raise UserError(_('The order has no products.'))

        message_body = self.whatsapp_message_body()
        message_view = self.whatsapp_message_view('\n')
        message_history = self.whatsapp_message_view('<br>')
        affair = _('Quotation %s') %(self.name)
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
                        'default_object_origin': 'sale.order',
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
        response += _('Your quotation *%s* %s%s\n') %(self.name,linefeed,linefeed)
        response += _('*DETAIL* %s\n') % (linefeed)
        for line in self.order_line:
            response += _('*%s*%s\n') % (line.name_short,linefeed)
            response += _('_Cant:_  %s%s_P.unit:_ %s%s%s_Total:_ %s%s%s\n') % (str(line.product_qty),tab,self.currency_id.symbol,str((float("{:.2f}".format(line.price_unit)))),tab,self.currency_id.symbol,(float("{:.2f}".format(line.price_total))),linefeed)
        response += linefeed +'\n'
        response += _('Amount: %s*%s %s* %s\n') % (tab,self.currency_id.symbol,self.amount_untaxed,linefeed)
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
        response += _('Your quotation %s%s') %(self.name,linefeed)
        response += _('DETAIL%s') % (linefeed)
        for line in self.order_line:
            response += _('%s%s') % (line.name_short,linefeed)
            response += _('Cant:%s  P.unit:%s%s  Total:%s%s%s') % (str(line.product_qty),self.currency_id.symbol,str((float("{:.2f}".format(line.price_unit)))),self.currency_id.symbol,(float("{:.2f}".format(line.price_total))),linefeed)
        response += linefeed
        response += _('Amount: %s %s %s') % (self.currency_id.symbol,self.amount_untaxed,linefeed)
        response += _('Tax: %s %s %s') % (self.currency_id.symbol,self.amount_tax,linefeed)
        response += '----------------------------------' + linefeed
        response += _('Amount Total: %s %s') % (self.currency_id.symbol,self.amount_total)
        return response

    def messagge_email_data(self,body):
        MailMessage_sudo = self.env['mail.message'].sudo()
        parent_message = MailMessage_sudo.search([('res_id', '=', self.id), ('model', '=', 'sale.order'), ('message_type', '!=', 'user_notification')], order="id ASC", limit=1)
        # email_data = self._message_compute_author(None, None, raise_exception=True)
        subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')
        values_list = []
        values = {}
        # values['author_id'] = email_data['author_id']  
        # values['email_from'] =email_data['email_from'] 
        values['model']='sale.order'
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

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    name_short = fields.Char(compute="_compute_name_short")
    product_qty = fields.Float(compute='_compute_product_qty', string='Product Qty', digits='Product Unit of Measure')

    @api.depends('product_id.display_name')
    def _compute_name_short(self):
        """ Compute a short name for this sale order line, to be used on the website where we don't have much space.
            To keep it short, instead of using the first line of the description, we take the product name without the internal reference.
        """
        for record in self:
            record.name_short = record.product_id.with_context(display_default_code=False).display_name

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_product_qty(self):
        for line in self:
            if not line.product_id or not line.product_uom or not line.product_uom_qty:
                line.product_qty = 0.0
                continue
            line.product_qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
