# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__) 

class mod_request_requirements(models.Model):
    _name = 'mod.request.requirements'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'analytic.mixin']
    _description = _("Detail of the requirements")

    _order = 'create_date desc'

    LIST_TAG = [
        ('pending', 'Pendiente'),
        ('supported', 'Sustentado')
    ]

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
    repayment_id = fields.Many2one('mod.request.repayment', string='Repayment')
    liquidation_generated = fields.Boolean(string='Liquidation Generated', default=False)
    amount_total = fields.Float(string="Amount", compute='_compute_amounts', tracking=4)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica')
    qty_sin_sustentar = fields.Float(compute='get_qty_sin_sustentar', copy=False)
    qty_sustentada = fields.Float(compute='get_qty_sin_sustentar', copy=False)
    amount_qty_sin_sustentar = fields.Float(string="Monto sin sustentar", compute='_compute_amounts', tracking=4)
    amount_qty_sustentada = fields.Float(string="Monto sustentado", compute='_compute_amounts', tracking=4)
    sustentado = fields.Boolean(compute='get_qty_sin_sustentar')
    tag_sustentado = fields.Selection(LIST_TAG, string = 'Sustentado' ,default='pending')


    def get_qty_sin_sustentar(self):
        supported_obj = self.env['mod.request.upload.judicial.supported']
        for rec in self:
            support = supported_obj.search([('requirement_id','=',rec.id)])
            qty_sustentado = 0
            for s in support:
                qty_sustentado += sum([s.amount])
            rec.qty_sin_sustentar = rec.amount_requirement - qty_sustentado
            rec.qty_sustentada = qty_sustentado
            rec.sustentado = rec.qty_sin_sustentar <= 0


    # def write(self, vals):
    #     res = super(mod_request_requirements, self).write(vals)
    #     if self.sustentado:
    #         self.tag_sustentado = 'completed'
    #     return res




    def _compute_count_payment(self):
        for rec in self:
            if rec.liquidation_id:
                rec.liqui_count = 1
            else:
                rec.liqui_count = 0
                rec.liquidation_generated = False

    liqui_count = fields.Integer(string="Contador de Liquidación", compute="_compute_count_payment")
    liquidation_id = fields.Many2one('mod.request.liquidation.sheet', 'Liquidación')
    state_liquidation = fields.Selection(related='liquidation_id.state')

    

    # DNINACO
    product_id = fields.Many2one('product.product', 'Producto Gasto')


    @api.depends('amount_requirement')
    def _compute_amounts(self):
        for rec in self:
            rec.amount_total = rec.amount_requirement
            rec.amount_qty_sin_sustentar = rec.qty_sin_sustentar
            rec.amount_qty_sustentada = rec.qty_sustentada


    def name_get(self):
        result = []
        for rec in self:
            if self.env.context.get('name_rq', False):
                result.append((rec.id,'%s / %s' % (rec.mod_request_id.name, rec.name_requirement)))
            else:
                result.append((rec.id,'%s' % (rec.name_requirement)))
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

        list_user = []
        cr = self.env.cr
        user_id = self.env['res.users'].browse(self._uid).id
        group_assistant = self.env['ir.model.data']._xmlid_lookup('mod_request.mod_request_group_manager_assistant')[2]
        query_group = """
                        select uid from res_groups_users_rel
                            where gid = %s
                        """
        cr.execute(query_group,(group_assistant,))
        g_active = cr.fetchall()
        for g in g_active:
            list_user.append(g[0])
        if user_id in list_user:
            raise UserError('No tiene permisos para realizar esta acción')
        else:
            data_liquidation_sheet = {
                # 'name':self.name,
                # 'employee_id':employe_id.id,
            }
            liquidation_sheet_id = liquidation_sheet_env.create(data_liquidation_sheet)


            for line in self:
                if line.mod_request_id.state != 'complete':
                    raise UserError(_("Solo debe Seleccionar Solicitudes en estado Completado"))

                if line.repayment_id.for_liquidation == False:
                    raise UserError(_("Sólo puede generar liquidacion de tipo de gasto reembolsable"))
                # if line.liquidation_generated:
                if line.state_liquidation:
                    raise UserError(_("Requerimiento ya tiene liquidacion %s - %s" %(line.mod_request_id.name,line.name_requirement)))
                data_liquidation_sheet_line = {
                    'request_id':line.mod_request_id.id,
                    'name':line.name_requirement,
                    'case':line.case_requirement,
                    'proceedings':line.proceedings_requirement,
                    # 'date':line.date_request_requirement,
                    'court_entity':line.court_entity_requirement,
                    'ruc_dni':line.ruc_dni_requirement,
                    'description':line.description_requirement,
                    'partner_id':line.partner_id.id,
                    'amount':line.amount_requirement,
                    'liquidation_sheet_id':liquidation_sheet_id.id
                }
                liquidation_sheet_line_env.create(data_liquidation_sheet_line)
                line.liquidation_generated = True
            self.liquidation_id = liquidation_sheet_id.id

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
    

    def view_liquidation(self, liquidation=False):
        if not liquidation:
            self.sudo()._read(['liquidation_id'])
            liquidation = self.liquidation_id

        result = self.env['ir.actions.act_window']._for_xml_id('mod_request.mod_request_action_liquidation_report')
        
        if liquidation:
            res = self.env.ref('mod_request.view_liquidation_sheet_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = liquidation.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result
            

