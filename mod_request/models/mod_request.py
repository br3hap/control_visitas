# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests
from odoo.http import request
from odoo.exceptions import UserError
import base64
from datetime import datetime, date
import logging
_logger = logging.getLogger(__name__)   

class mod_request(models.Model):
    _name = 'mod.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'analytic.mixin']
    _description = _("Requirements and Request")

    _order = 'create_date desc'

    LIST_PROCESS_REQUEST = [
        ('purchase', 'Purchase'),
        ('transfer', 'Transfer'),
        ('repayment', 'Repayment')
    ]

    LIST_FORMAT_REQUEST = [
        ('general', 'General'),
        ('customized', 'Customized')
    ]

    LIST_TYPE_REQUEST = [
        ('judicial', 'Judicial'),
        ('administrative', 'Administrative'),
        ('others', 'Others')
    ]

    LIST_STATE = [
        ('pending', 'Pending'),
        ('subscriber', 'Subscriber'),
        ('support_to_approve','Support to approve'),
        ('supported', 'Supported'),
        ('complete', 'Complete'),
        ('refused', 'Refused'),
        ('to_correct', 'To correct'),
        ('cancel', 'Cancel')
    ]

    READONLY_STATES = {
        'subscriber': [('readonly', True)],
        'supported': [('readonly', True)],
        'support_to_approve': [('readonly', True)],
        'complete': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    LIST_EXPENSE = [
        ('pending','Pending'),
        ('generated','Generated'),
    ]

    LIST_LIQUIDATION = [
        ('pending','Pending'),
        ('generated','Generated'),
    ]

    _sql_constraints = [('name_unique', 'unique(name)','name already exists')]


    name = fields.Char(string='Name Request', index=True,
                       copy=False, default=lambda self: _('New'), states=READONLY_STATES)
    name_applicant = fields.Char(
        string='Applicant name', tracking=True, states=READONLY_STATES)
    process_request = fields.Selection(
        LIST_PROCESS_REQUEST, string='Request process', index=True, tracking=True, states=READONLY_STATES)

    # format_request = fields.Selection(
    #     LIST_FORMAT_REQUEST, string='Format', tracking=True, default='general', states=READONLY_STATES)
    format_request = fields.Char(string='Format', tracking=True, states=READONLY_STATES)
    description = fields.Text(string='Description', states=READONLY_STATES)
    seller = fields.Many2one('hr.employee', string='Seller', tracking=True,
                             default=lambda self: self.env.uid, states=READONLY_STATES)
    type_request = fields.Selection(
        LIST_TYPE_REQUEST, string='Type Request', tracking=True, default='judicial', states=READONLY_STATES)
    date_request = fields.Datetime(string='Date Request', copy=False,
                                   default=lambda self: fields.datetime.now(), states=READONLY_STATES)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id.id, states=READONLY_STATES)
    partner_id = fields.Many2one(
        'res.partner', string='Partner', states=READONLY_STATES)
    state = fields.Selection(LIST_STATE, string='Status', default='pending', copy=False,
                             index=True, readonly=True, store=True, tracking=True, help='Status of the request.')
    file_request = fields.Binary(
        string='File', tracking=True, states=READONLY_STATES)
    file_name = fields.Char(string='File Name')
    amount = fields.Float(string='Amount', tracking=True,
                          states=READONLY_STATES)
    amount_compute = fields.Float(string='Amount', compute='_compute_amount')
    amount_total = fields.Monetary(string="Amount", compute='_compute_amounts', tracking=4)
    bank = fields.Char(string='Bank', states=READONLY_STATES)
    account = fields.Char(string='Account', states=READONLY_STATES)
    mod_request_requirements_ids = fields.One2many(
        'mod.request.requirements', 'mod_request_id', string='Requirements', copy=True)
    # type_state = fields.Char(
    #     string='Type state', compute='_compute_type_state')
    file_purchased_ids = fields.One2many(
        'mod.request.upload.judicial.purchased', 'mod_request_id')
    file_supported_ids = fields.One2many(
        'mod.request.upload.judicial.supported', 'mod_request_id')
    # checklist_puchased = fields.Boolean(string="CheckList Purchased", default=False, tracking=True)
    # observation_purchased = fields.Text(string="Observation")
    checklist_supported = fields.Boolean(string="CheckList Supported", default=False, tracking=True)
    observation_supported = fields.Text(string="Observation")
    date_supported = fields.Datetime(string="Date Supported")
    attach_purchase = fields.Boolean(string='Attach Purchase')
    attach_support = fields.Boolean(string='Attach Support')
    expense_generated = fields.Selection(LIST_EXPENSE, string='Expense Generated', default='pending')
    # liquidation_generated = fields.Selection(LIST_LIQUIDATION, string='Liquidation Generated', default='pending')
    # liquidation_generated_b = fields.Boolean(string='Liquidation Generated', default=False)
    
    # DNINACO
    def _compute_count_payment(self):
        for order in self:
            if order.payment_id:
                order.payment_count = 1
            else:
                order.payment_count = 0

    payment_count = fields.Integer(string="Contador de Gasto", compute="_compute_count_payment")
    payment_id = fields.Many2one('account.payment', 'Pago')
    num_operation = fields.Char('Número de Operación')

    # DNINACO
    def view_payment(self, payment=False):
        if not payment:
            self.sudo()._read(['payment_id'])
            payment = self.payment_id

        result = self.env['ir.actions.act_window']._for_xml_id('account.action_account_payments')
        
        if payment:
            res = self.env.ref('account.view_account_payment_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = payment.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result

    #DNINACO
    def action_masive_paid(self):
        account_pen = int(self.env['ir.config_parameter'].sudo().get_param('mod_request.account_expenses_pen'))
        account_usd = int(self.env['ir.config_parameter'].sudo().get_param('mod_request.account_expenses_usd'))

        amount = 0
        currency_id = False
        account_id = None
        for rec in self.browse(self._context.get('active_ids')):
            if rec.state != 'pending':
                raise UserError(_("Solo debe Seleccionar Solicitudes en estado Pendiente"))
            if currency_id:
                if currency_id != rec.currency_id.id:
                    raise UserError(_("Solo debe Seleccionar Solicitudes de una misma Moneda"))
            else:
                currency_id = rec.currency_id.id
                if rec.currency_id.name == 'PEN':
                    account_id = account_pen
                else:
                    account_id = account_usd
                    
            amount = amount+rec.amount_compute
        action = self.env["ir.actions.actions"]._for_xml_id("mod_request.mod_request_masive_paid_action")
        action['context'] = {'default_amount': amount,'default_account_id':account_id, 'active_domain': self._context.get('active_ids')}
        action['views'] = [(self.env.ref('mod_request.view_mod_request_masive_paid_form').id, 'form')]
        return action

    # DNINACO
    def _compute_count_expense(self):
        for order in self:
            if order.expense_sheet_id:
                order.expense_count = 1
            else:
                order.expense_count = 0
                order.ocultar_create_expense=False

    expense_count = fields.Integer(string="Contador de Gasto", compute="_compute_count_expense")
    expense_sheet_id = fields.Many2one('hr.expense.sheet')
    ocultar_create_expense = fields.Boolean('Ocultar Gasto')

    # DNINACO
    def view_expenses(self, expenses=False):
        if not expenses:
            self.sudo()._read(['expense_sheet_id'])
            expenses = self.expense_sheet_id

        result = self.env['ir.actions.act_window']._for_xml_id('hr_expense.action_hr_expense_sheet_all_all')
        
        if expenses:
            res = self.env.ref('hr_expense.view_hr_expense_sheet_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = expenses.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result

    # DNINACO
    def create_expense(self):

        expense_sheet_env = self.env['hr.expense.sheet']
        employee_env = self.env['hr.employee']
        hr_expense_env = self.env['hr.expense']
        invoice_expense_env = self.env['invoice.expense']
        is_enable = self.env['ir.config_parameter'].sudo().get_param('mod_request.allow_shortening_processes', default=False)
        
        employe_id = self.seller
        if not employe_id:
            raise UserError(_("No existe Empleado Configurado para el Vendedor Seleccionado"))

        fecha_expense_sheet = str(self.date_request.year)+"-"+str(self.date_request.month)+"-"+str(self.date_request.day)

        data_expense_sheet = {
                'name': self.name,
                'employee_id': employe_id.id,
                'payment_mode': 'company_account',
                'accounting_date': fecha_expense_sheet,
        }
        
        expense_sheet_id = expense_sheet_env.create(data_expense_sheet)
        self.expense_sheet_id = expense_sheet_id.id
        self.ocultar_create_expense = True
        self.expense_generated = 'generated'
        
        for line in self.mod_request_requirements_ids:

            fecha_expense = str(line.date_request_requirement.year)+"-"+str(line.date_request_requirement.month)+"-"+str(line.date_request_requirement.day)
            
            if not line.product_id and not line.account_move_id:
                raise UserError(_("Debe Seleccionar los Gastos Amarrados a los Requerimientos"))
            
            if line.product_id:
                data_expense = {
                                'name': line.name_requirement,
                                'employee_id': employe_id.id,
                                'payment_mode': 'company_account',
                                'total_amount': line.amount_requirement,
                                'date': fecha_expense,
                                'accounting_date': fecha_expense,
                                'product_id': line.product_id.id,
                                'sheet_id': self.expense_sheet_id.id,
                                # 'people_id':line.partner_id.id
                }
                hr_expense_env.create(data_expense)

            elif line.account_move_id:
                data_invoice = {
                    'descripcion':line.name_requirement,
                    'invoice_id':line.account_move_id.id,
                    'amount_company':line.account_move_id.amount_residual,
                    'amount_total':line.amount_requirement,
                    'expense_sheet_id':self.expense_sheet_id.id,

                }
                invoice_expense_env.create(data_invoice)

            if is_enable:
                expense_sheet_id.action_submit_sheet()
                expense_sheet_id.approve_expense_sheets()
                expense_sheet_id.paid_expense()
                expense_sheet_id.action_sheet_move_create()

        return {
            'name': _('test'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id':expense_sheet_id.id,
            'view_id': self.env.ref('invoice_expense.view_hr_expense_sheet_form_inherit').id,
            'res_model': 'hr.expense.sheet',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
                # expense_sheet_id.action_sheet_move_create()
                # _logger.warning("si llegócreate")
                # expense_sheet_id.action_register_payment()
                # _logger.warning("ya no llegó")
                
    # DNINACO CREACION MASIVA DE UN GASTO PARA VARIAS SOLICITUDES
    def action_masive_expenses(self):
        expense_sheet_env = self.env['hr.expense.sheet']
        employee_env = self.env['hr.employee']
        hr_expense_env = self.env['hr.expense']
        invoice_expense_env = self.env['invoice.expense']
        is_enable = self.env['ir.config_parameter'].sudo().get_param('mod_request.allow_shortening_processes', default=False)
        
        # VALIDACION DE ESTADOS Y DE MISMO VENDEDOR
        employe_id = False
        name = 'Informe de Gasto ('
        for rec in self.browse(self._context.get('active_ids')):
            if not rec.seller.id:
                raise UserError(_("Todas las Solicitudes deben Contener el Campo Vendedor Registrado"))
            if rec.state != 'supported':
                raise UserError(_("Solo debe Seleccionar Solicitudes en estado Sustentado"))
            if employe_id:
                name = name+','+rec.name
                if employe_id != rec.seller.id:
                    raise UserError(_("Solo debe Seleccionar Solicitudes de una mima Persona Asignada"))
            else:
                name = name+rec.name
                employe_id = rec.seller.id
        
        name = name+")"

        # CREACION DE GASTOS
        fecha_expense_sheet = date.today()

        data_expense_sheet = {
                'name': name,
                'employee_id': employe_id,
                'payment_mode': 'company_account',
                'accounting_date': fecha_expense_sheet,
        }
        expense_sheet_id = expense_sheet_env.create(data_expense_sheet)
        
        # RECORREMOS, ASIGNAMOS EL GASTO GENERADO y GENERAMOS LAS LINEAS DE GASTO
        for rec in self.browse(self._context.get('active_ids')):
            rec.expense_sheet_id = expense_sheet_id.id
            rec.ocultar_create_expense = True
            rec.expense_generated = 'generated'
        
            for line in rec.mod_request_requirements_ids:

                fecha_expense = str(line.date_request_requirement.year)+"-"+str(line.date_request_requirement.month)+"-"+str(line.date_request_requirement.day)
                
                if not line.product_id and not line.account_move_id:
                    raise UserError(_("Debe Seleccionar los Gastos Amarrados a los Requerimientos"))
                
                if line.product_id:
                    data_expense = {
                                    'name': line.name_requirement,
                                    'employee_id': employe_id,
                                    'payment_mode': 'company_account',
                                    'total_amount': line.amount_requirement,
                                    'date': fecha_expense,
                                    'accounting_date': fecha_expense,
                                    'product_id': line.product_id.id,
                                    'sheet_id': expense_sheet_id.id,
                                    # 'people_id':line.partner_id.id
                    }
                    hr_expense_env.create(data_expense)

                elif line.account_move_id:
                    data_invoice = {
                        'descripcion':line.name_requirement,
                        'invoice_id':line.account_move_id.id,
                        'amount_company':line.account_move_id.amount_residual,
                        'amount_total':line.amount_requirement,
                        'expense_sheet_id':expense_sheet_id.id,

                    }
                    invoice_expense_env.create(data_invoice)

        if is_enable:
            expense_sheet_id.action_submit_sheet()
            expense_sheet_id.approve_expense_sheets()
            expense_sheet_id.paid_expense()
            expense_sheet_id.action_sheet_move_create()
        
        return {
                'name': _('test'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_id':expense_sheet_id.id,
                'view_id': self.env.ref('invoice_expense.view_hr_expense_sheet_form_inherit').id,
                'res_model': 'hr.expense.sheet',
                'type': 'ir.actions.act_window',
                'target': 'current',
            }



    @api.depends('mod_request_requirements_ids.amount_requirement')
    def _compute_amounts(self):
        for rec in self:
            rec.amount_total = rec.amount_compute


    # def action_in_progress(self):
    #     if self.type_request == 'administrative' and self.process_request in ('purchase','transfer'):
    #         self.validate_fields_pro_fact()
    #     self.write({'state': 'in_progress'})
    #     self.api_onchange_status(self.name, 'en proceso')


    def action_subscriber(self):
        self.write({'state': 'subscriber'})
        self.api_onchange_status(self.name, 'abonado')


    # def action_purchased(self):
    #     if self.checklist_puchased:
    #         self.write({'state': 'purchased'})
    #         self.api_onchange_status(self.name, 'comprado')
    #     else:
    #         raise UserError(_("Unvalidated Files"))


    def action_support_to_approve(self):
        self.write({'state':'support_to_approve'})
        self.date_supported = datetime.now()


    def action_supported(self):
            if self.checklist_supported:
                self.validate_fields_pro_fact()
                self.write({'state': 'supported'})
                self.api_onchange_status(self.name, 'sustentado')                
            else:
                raise UserError(_("Unvalidated Files"))
        # if len(self.file_supported_ids) >= 1:
        #     self.write({'state': 'supported'})
        #     self.api_onchange_status(self.name, 'sustentado')
        # if self.checklist_supported:
        #     self.validate_fields_pro_fact()
        #     self.write({'state': 'supported'})
        #     self.api_onchange_status(self.name, 'sustentado')
        #     self.date_supported = datetime.now()
        # else:
        #     # raise UserError(_("No support files"))
        #     raise UserError(_("Unvalidated Files"))


    def action_complete(self):
        # if self.type_request == 'administrative' and self.process_request in ('purchase','transfer'):
        #     self.validate_fields_pro_fact()
        # if not self.expense_sheet_id:
        #     raise UserError(_('Generate expense report'))

        # if self.expense_sheet_id.state == 'done':
        #     print("Si está pagado")
        #     self.write({'state': 'complete'})
        #     self.api_onchange_status(self.name, 'completado')
        # else:
        #     raise UserError(_("Aun no está pagado"))

        self.write({'state': 'complete'})
        self.api_onchange_status(self.name, 'completado')



    def action_refused(self):
        self.write({'state': 'refused'})
        self.api_onchange_status(self.name, 'rechazado')


    def action_to_correct(self):
        self.write({'state': 'to_correct'})
        self.api_onchange_status(self.name, 'por corregir')


    def action_cancel(self):
        self.write({'state': 'cancel'})
        self.api_onchange_status(self.name, 'cancelado')
        

    def action_pending(self):
        # self.checklist_puchased = False
        self.checklist_supported = False
        self.attach_purchase = False
        self.attach_support = False
        # self.observation_purchased = ''
        self.observation_supported = ''
        self.write({'state': 'pending'})
        self.api_onchange_status(self.name, 'pendiente')


    def action_corrected(self):
        self.write({'state': 'supported'})
        self.api_onchange_status(self.name, 'sustentado')


    @api.onchange('type_request')
    def _onchange_type_request(self):

        for rec in self.mod_request_requirements_ids:
            self.mod_request_requirements_ids = [(3, rec.id)]

        if self.type_request == 'administrative':
            self.partner_id = self.env.company.id
        else:
            self.partner_id = ''


    # @api.onchange('process_request', 'state', 'type_request')
    # def _compute_type_state(self):
    #     for rec in self:
    #         if rec.process_request != 'repayment' and rec.state in ('pending') and rec.type_request in ('judicial'):
    #             rec.type_state = 'repayment_p_j'
    #         # elif rec.process_request != 'repayment' and rec.state in ('in_progress') and rec.type_request in ('judicial'):
    #         #     rec.type_state = 'repayment_i_j'
    #         # elif rec.process_request in 'repayment' and rec.state in ('pending') and rec.type_request in ('judicial'):
    #         #     rec.type_state = 'repayment_pe_j'
    #         # elif rec.process_request in ('purchase','transfer') and rec.state in ('pending') and rec.type_request in ('administrative'):
    #         #     rec.type_state = 'pending_administrative'
    #         else:
    #             rec.type_state = ''


    def _compute_amount(self):
        for rec in self:
            if rec.type_request == 'administrative':
                rec.amount_compute = rec.amount
            else:
                rec.amount_compute = sum(
                    [i.amount_requirement for i in rec.mod_request_requirements_ids])


    def api_onchange_status(self, cod_request, status):
        route = self.env['rest.api.url'].search(
            [('name', '=', 'url_status')], limit=1)
        
        token = self.env['rest.api.token'].search(
            [('name', '=', 'token_change_status')], limit=1)
         
        user = self.env.user.login
        user_split = user.split('@')[0]

        data = {
            "token": token.account_token,
            "requestCode": cod_request,
            "status": status,
            "user": user_split
        }

        try:
            response = requests.put(route.url, json=data)
            if response.status_code == 200:
                # print("El estado se cambió exitosamente en el otro sistema.")
                _logger.warning("El estado se cambió exitosamente en el otro sistema.")
            else:
                # print("Error al cambiar el estado. Código de respuesta:",
                #       response.status_code)
                _logger.warning("Error al cambiar el estado. Código de respuesta:",response.status_code)
                # print("Mensaje de error:", response.text)
                _logger.warning("Mensaje de error:", response.text)

        except requests.exceptions.RequestException as e:
            # print("Error al realizar la solicitud:", e)
            _logger.warning("Error al realizar la solicitud:", e)

        return data

    
    def back_function(self):
        if self.type_request in ('judicial','others') and self.process_request in ('purchase','transfer'):

            if self.state == 'subscriber':
                self.state = 'pending'
                self.api_onchange_status(self.name, 'pendiente')

            # elif self.state == 'purchased':
            #     self.state = 'subscriber'
            #     self.checklist_puchased = False
            #     self.attach_purchase = False
            #     self.observation_purchased = ''
            #     self.api_onchange_status(self.name, 'abonado')

            elif self.state == 'support_to_approve':
                self.state = 'subscriber'
                self.checklist_supported = False
                self.attach_support = False
                self.observation_supported = ''

            elif self.state == 'supported':
                self.state = 'subscriber'
                self.checklist_supported = False
                self.attach_support = False
                self.observation_supported = ''
                self.api_onchange_status(self.name, 'subscriber')

            # elif self.state == 'supported':
            #     self.state = 'purchased'
            #     self.api_onchange_status(self.name, 'comprado')

            elif self.state == 'complete':
                self.state = 'supported'
                self.api_onchange_status(self.name, 'sustentado')

            elif self.state == 'to_correct':
                self.state = 'supported'
                self.api_onchange_status(self.name, 'sustentado')

        elif self.type_request in ('judicial','others') and self.process_request in ('repayment'):

            if self.state == 'complete':
                self.state = 'pending'
                self.api_onchange_status(self.name, 'pendiente')


        elif self.type_request == 'administrative' and self.process_request in ('purchase','transfer'):
            
            if self.state == 'complete':
                self.state = 'pending'
                self.api_onchange_status(self.name, 'pendiente')



    
    # def api_upload_image(self, cod_request):

    #     route = self.env['rest.api.url'].search([('name', '=', 'url_status')], limit=1)
    #     token = self.env['rest.api.token'].search([('name', '=', 'token_change_status')], limit=1)

    #     user = self.env.user.login
    #     user_split = user.split('@')[0]

    #     data = {}
    #     for rec in self:
    #         files_data = []
    #         for img in rec.file_purchased_ids:
    #             image_url = img.file_purchased
    #             file_content = base64.b64encode(image_url).decode()

    #             files_data.append({
    #                 "fileName": img.file_name_purchased,
    #                 "base64": file_content
    #             })

    #         data = {
    #             "token": token.account_token,
    #             "requestCode": cod_request,
    #             "status": "comprado",
    #             "user": user_split,
    #             "files": files_data
    #         }
    #     print("data", data)

    #     try:
    #         response = requests.put(route.url, json=data)
    #         if response.status_code == 200:
    #             print("Se envió correctamente los archivos de compra.")
    #         else:
    #             print("Error al subir archivos. Código de respuesta:", response.status_code)
    #             print("Mensaje de error:", response.text)

    #     except requests.exceptions.RequestException as e:
    #         print("Error al realizar la solicitud:", e)

    #     return data



    def function_image(self):
        for rec in self:
            # self.api_upload_image(rec.name)
            for up in rec.file_purchased_ids:
                up.state = True



    def show_window_checklist_supported(self):
        values = {
            'id':'mod_request_form_check_list_supported',
            'name':_('Validate Supported File'),
            'view_type':'form',
            'view_mode':'form',
            'target':'new',
            'context':{
                'get_cod':self.id,
                'get_observation_supported':self.observation_supported,
                'get_checklist_supported':self.checklist_supported,
                'get_attach_support':self.attach_support,
            },
            'res_model':'mod.request.checklist.supported.wizard',
            'type':'ir.actions.act_window'
        }

        return values
    

    @api.model
    def create(self, values):
       res = super(mod_request, self).create(values)
       requirement_env = self.env['mod.request.requirements']

       data_request = {
                'mod_request_id':res.id,
                'name_requirement':'REQ-001',
                'case_requirement':'',
                'proceedings_requirement':'',
                'amount_requirement':res.amount,
                'date_request_requirement':res.date_request,
                'court_entity_requirement':'',
                'ruc_dni_requirement':'',
                'description_requirement':res.description,
                'json_text':''
            }
       if res.type_request == 'administrative':
            requirement_env.create(data_request)

       return res
    

    
    def write(self, values):
        res = super(mod_request, self).write(values)
        _logger.warning("requirement_env",self.mod_request_requirements_ids)
        if self.type_request == 'administrative':
            for rq in self.mod_request_requirements_ids:
                rq.amount_requirement=self.amount
        return res


    def validate_fields_pro_fact(self):
        if not self.mod_request_requirements_ids:
            raise UserError(_("Add Requirement"))
        for rec in self.mod_request_requirements_ids:
            if not rec.product_id  and not rec.account_move_id:
                raise UserError(_("Empty product or invoice fields"))
            
    
    # @api.model
    # def action_generate_liquidation(self):
    #     liquidation_sheet_env = self.env['mod.request.liquidation.sheet']
    #     liquidation_sheet_line_env = self.env['mod.request.liquidation.sheet.line']
    #     employe_id = self.seller
    #     data_liquidation_sheet = {
    #         # 'name':self.name,
    #         # 'employee_id':employe_id.id,
    #     }
    #     liquidation_sheet_id = liquidation_sheet_env.create(data_liquidation_sheet)

    #     for rec in self.browse(self._context.get('active_ids')):
    #         if rec.state != 'complete':
    #             raise UserError(_("Solo debe Seleccionar Solicitudes en estado Completado"))

    #         rec.liquidation_generated_b = True


    #     for line in self.mod_request_requirements_ids:
    #         data_liquidation_sheet_line = {
    #             'request_id':line.mod_request_id.id,
    #             'name':line.name_requirement,
    #             'case':line.case_requirement,
    #             'proceedings':line.proceedings_requirement,
    #             'date':line.date_request_requirement,
    #             'court_entity':line.court_entity_requirement,
    #             'ruc_dni':line.ruc_dni_requirement,
    #             'description':line.description_requirement,
    #             'partner_id':line.partner_id.id,
    #             'amount':line.amount_requirement,
    #             'liquidation_sheet_id':liquidation_sheet_id.id
    #         }
    #         liquidation_sheet_line_env.create(data_liquidation_sheet_line)

    #     return {
    #             'name': _('test'),
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_id':liquidation_sheet_id.id,
    #             'view_id': self.env.ref('mod_request.view_liquidation_sheet_form').id,
    #             'res_model': 'mod.request.liquidation.sheet',
    #             'type': 'ir.actions.act_window',
    #             'target': 'current',
    #         }
            
