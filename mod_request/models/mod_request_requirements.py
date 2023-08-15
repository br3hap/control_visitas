# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class mod_request_requirements(models.Model):
    _name = 'mod.request.requirements'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'analytic.mixin']
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
    state = fields.Selection(related="mod_request_id.state")
    is_repayment = fields.Boolean(string='Is Repayment')
    liquidation_generated = fields.Boolean(string='Liquidation Generated', default=False)
    amount_total = fields.Float(string="Amount", compute='_compute_amounts', tracking=4)

    

    # DNINACO
    product_id = fields.Many2one('product.product', 'Producto Gasto')


    @api.depends('amount_requirement')
    def _compute_amounts(self):
        for rec in self:
            rec.amount_total = rec.amount_requirement


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


    # @api.model
    def action_generate_liquidation(self):
        liquidation_sheet_env = self.env['mod.request.liquidation.sheet']
        liquidation_sheet_line_env = self.env['mod.request.liquidation.sheet.line']
        data_liquidation_sheet = {
            # 'name':self.name,
            # 'employee_id':employe_id.id,
        }
        liquidation_sheet_id = liquidation_sheet_env.create(data_liquidation_sheet)

        # for rec in self.browse(self._context.get('active_ids')):
        #     if rec.state != 'complete':
        #         raise UserError(_("Solo debe Seleccionar Solicitudes en estado Completado"))

        #     rec.liquidation_generated_b = True


        for line in self:
            if line.mod_request_id.state != 'complete':
                raise UserError(_("Solo debe Seleccionar Solicitudes en estado Completado"))
            if line.liquidation_generated:
                raise UserError(_("Requerimiento ya tiene liquidacion %s - %s" %(line.mod_request_id.name,line.name_requirement)))
            data_liquidation_sheet_line = {
                'request_id':line.mod_request_id.id,
                'name':line.name_requirement,
                'case':line.case_requirement,
                'proceedings':line.proceedings_requirement,
                'date':line.date_request_requirement,
                'court_entity':line.court_entity_requirement,
                'ruc_dni':line.ruc_dni_requirement,
                'description':line.description_requirement,
                'partner_id':line.partner_id.id,
                'amount':line.amount_requirement,
                'liquidation_sheet_id':liquidation_sheet_id.id
            }
            liquidation_sheet_line_env.create(data_liquidation_sheet_line)
            line.liquidation_generated = True

        return {
                'name': _('test'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_id':liquidation_sheet_id.id,
                'view_id': self.env.ref('mod_request.view_liquidation_sheet_form').id,
                'res_model': 'mod.request.liquidation.sheet',
                'type': 'ir.actions.act_window',
                'target': 'current',
            }
            

