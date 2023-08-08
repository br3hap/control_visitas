# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class crm_lead(models.Model):
    _inherit = 'crm.lead'

    @api.depends('partner_id','enable_whatsapp')
    def _enable_whatsapp(self):
        is_enable = self.env['ir.config_parameter'].sudo().get_param('whatsapp.whatsapp_enable', default=False)
        is_enable_crm = self.env['ir.config_parameter'].sudo().get_param('whatsapp_crm.whatsapp_enable_crm', default=False)
        for wsp in self:
            if wsp and is_enable and is_enable_crm:
                wsp.enable_whatsapp = True
            else:
                wsp.enable_whatsapp = False

    enable_whatsapp = fields.Boolean(compute='_enable_whatsapp', string='enable whatsapp')

    def whatsapp_send_crm(self):
        url = self.env['ir.config_parameter'].sudo().get_param('whatsapp.whatsapp_enable', default=False)
        if not url:
            return
        if not self.partner_id.mobile:
            raise UserError(_('first enter the partner mobile number.'))

        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': 
                    {
                        'default_user_id': self.partner_id.id,
                        'default_show_note':False,
                        'default_res_id': str(self.id),
                        'default_object_origin': 'crm.lead',
                    },
                }

    def messagge_email_data(self,body):
        MailMessage_sudo = self.env['mail.message'].sudo()
        parent_message = MailMessage_sudo.search([('res_id', '=', self.id), ('model', '=', 'crm.lead'), ('message_type', '!=', 'user_notification')], order="id ASC", limit=1)
        # email_data = self._message_compute_author(None, None, raise_exception=True)
        subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')
        values_list = []
        values = {}
        # values['author_id'] = email_data['author_id']  
        # values['email_from'] =email_data['email_from'] 
        values['model']='crm.lead'
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