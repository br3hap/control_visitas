# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


# class mod_request_check_list_purchased(models.TransientModel):
#     _name = 'mod.request.checklist.purchased.wizard'

#     cod_request = fields.Many2one('mod.request', string='Cod. Request')
#     observation_purchased = fields.Text(string="Observation")
#     checklist_puchased = fields.Boolean(string="CheckList Purchased")
#     attach_purchase = fields.Boolean(string='Attach Purchase')


#     def default_get(self, fields):
#         c = super(mod_request_check_list_purchased, self).default_get(fields)
#         cod_request = self._context['get_cod']
#         observation_purchased = self._context['get_observation_purchased']
#         checklist_puchased = self._context['get_checklist_puchased']
#         attach_purchase = self._context['get_attach_purchase']
#         c['cod_request'] = cod_request
#         c['observation_purchased'] = observation_purchased
#         c['checklist_puchased'] = checklist_puchased
#         c['attach_purchase'] = attach_purchase
#         return c

    
#     def save(self):
#         data = self.read()[0]
#         observation_purchased = data['observation_purchased']
#         checklist_puchased = data['checklist_puchased']
#         attach_purchase = data['attach_purchase']
#         cod_request = self._context['get_cod']
#         mod_request=self.env['mod.request'].search([('id','=',cod_request)])
#         mod_request.write({'observation_purchased':observation_purchased, 'checklist_puchased':checklist_puchased,'attach_purchase':attach_purchase})
#         mod_request.action_purchased()



class mod_request_check_list_supported(models.TransientModel):
    _name = 'mod.request.checklist.supported.wizard'

    cod_request = fields.Many2one('mod.request', string='Cod. Request')
    observation_supported = fields.Text(string="Observation")
    checklist_supported = fields.Boolean(string="CheckList Supported")
    attach_support = fields.Boolean(string='Attach Support')


    def default_get(self, fields):
        c = super(mod_request_check_list_supported, self).default_get(fields)
        cod_request = self._context['get_cod']
        observation_supported = self._context['get_observation_supported']
        checklist_supported = self._context['get_checklist_supported']
        attach_support = self._context['get_attach_support']
        c['cod_request'] = cod_request
        c['observation_supported'] = observation_supported
        c['checklist_supported'] = checklist_supported
        c['attach_support'] = attach_support
        return c

    
    def save(self):
        data = self.read()[0]
        observation_supported = data['observation_supported']
        checklist_supported = data['checklist_supported']
        attach_support = data['attach_support']
        cod_request = self._context['get_cod']
        mod_request=self.env['mod.request'].search([('id','=',cod_request)])
        mod_request.write({'observation_supported':observation_supported, 'checklist_supported':checklist_supported, 'attach_support':attach_support})
        mod_request.action_supported()
	
	