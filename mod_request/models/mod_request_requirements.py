# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class mod_request_requirements(models.Model):
    _name = 'mod.request.requirements'
    _description = _("Detail of the requirements")

    _order = 'create_date desc'

    mod_request_id = fields.Many2one('mod.request', string='Cod. Request', ondelete='cascade')
    name_requirement = fields.Char(string='Cod. Requirement')
    case_requirement = fields.Char(string='Case')
    proceedings_requirement = fields.Char(string='Proceedings')
    amount_requirement = fields.Float(string='Amount')
    date_request_requirement = fields.Datetime(string='Date',copy = False, default = lambda self: fields.datetime.now())
    court_entity_requirement = fields.Char(string='Court / Entity')
    ruc_dni_requirement = fields.Char(string='RUC / DNI')
    description_requirement = fields.Char(string='Description')
    json_text = fields.Text(string='Json Text')
    account_move_id = fields.Many2one('account.move', string="Account Move")
    state_request = fields.Boolean(default = False, compute = '_compute_state_request')
    state_request_completed = fields.Boolean(default = False, compute = '_compute_state_request_completed')
    # state_request_purchased = fields.Boolean(default = False, compute = '_compute_state_request_purchased')
    partner_id = fields.Many2one(
        'res.partner', string='Partner')
    text_isnull = fields.Boolean(string='Text is Null', compute ='_compute_text_isnull')

    # DNINACO
    product_id = fields.Many2one('product.product', 'Producto Gasto')


    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id,'%s / %s' % (rec.mod_request_id.name, rec.name_requirement)))
        return result
    

    def _compute_state_request(self):
        for rec in self:
            if rec.mod_request_id.state not in ('pending'):
                rec.state_request = True
            else:
                rec.state_request = False

    
    def _compute_state_request_completed(self):
        for rec in self:
            if rec.mod_request_id.state in ('complete'):
                rec.state_request_completed = True
            else:
                rec.state_request_completed = False



    # def _compute_state_request_purchased(self):
    #     for rec in self:
    #         if rec.mod_request_id.state in ('purchased'):
    #             rec.state_request_purchased = True
    #         else:
    #             rec.state_request_purchased = False


    def show_text_json(self):
        values = {
            'id':'mod_requirement_form_json_text',
            'name':u'Json Text',
            'view_type':'form',
            'view_mode':'form',
            'target':'new',
            'context':{
                'get_json_text':self.json_text,
                'get_mod_requirement_id':self.id
            },
            'res_model':'mod.requirement.text.wizard',
            'type':'ir.actions.act_window',
        }

        return values


    def _compute_text_isnull(self):
        for rec in self:
            if rec.json_text is '':
                rec.text_isnull = True
            else:
                rec.text_isnull = False


    # def create(self, vals):
    #     res = super(mod_request_requirements, self).create(vals)
    #     if self.mod_request_id.type_request == 'administrative':
    #         print("is administrative")
    #     else:
    #         print("is judicial")
    #     return res

