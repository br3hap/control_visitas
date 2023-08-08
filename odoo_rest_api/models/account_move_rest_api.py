# -*- coding: utf-8 -*-
from unicodedata import name
from urllib import response
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import json
class AccountMoveResApi(models.Model):
    _name = 'account.move.rest.api'



    name = fields.Char(string='name')
    succes = fields.Boolean(strign="Succes")
    data_text = fields.Text(string="Json")
    response = fields.Text(string="Response")
    odoo_api_id = fields.Many2one(string='Odoo Api', comodel_name='odoo.rest.api')
    move_id = fields.Many2one(string='Invoice', comodel_name='account.move')
    journal_id = fields.Many2one(string='Payment Method', comodel_name='account.journal')
    payment_id = fields.Many2one(string='Payment', comodel_name='account.payment')
    date = fields.Date(string='Date',default=fields.Date.today())
    communication = fields.Char(string='Communication Payment')
    state = fields.Selection([
           ('draft', 'Draft'),
           ('posted', 'Posted'),
           ('paid_out','Paid out'),
       ], string='Status', default='draft')
    
    def concilie(self):
        account_move_lines_to_reconcile = self.env['account.move.line']
        for line in self.payment_id.move_line_ids + self.move_id.line_ids:
            if line.account_id.internal_type == 'receivable' and not line.reconciled:
                account_move_lines_to_reconcile |= line

            account_move_lines_to_reconcile.sudo().reconcile()
    def payment_api(self):

        total = self.move_id.amount_residual
        partner_type = False
        if self.move_id.partner_id:
            if total < 0:
                partner_type = 'supplier'
            else:
                partner_type = 'customer'

        payment_methods = (total>0) and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
        currency = self.journal_id.currency_id or  self.move_id.company_id.currency_id
        pay = self.env['account.payment'].search([('move_name','=',self.move_id.name)])

        data={
                        'payment_method_id': payment_methods and payment_methods[0].id or False,
                        'has_invoices': True,
                        'payment_type':'inbound' ,
                        'partner_id': self.move_id.partner_id.id or False,
                        'partner_type': 'customer',
                        'journal_id': self.journal_id.id,
                        "invoice_ids": [(6, 0,  self.move_id.ids)],
                        'payment_date': self.move_id.invoice_date,
                        'currency_id': currency.id,
                        'amount': abs(total),
                        'communication':self.communication if self.communication else self.move_id.name,
                        'company_id':self.move_id.id
                    }


        if pay:
            pay.write(data) 
            self.payment_id=pay.id
            if self.payment_id.state=='draft':
                pay.post()
            self.concilie()
            
        
        else:
            payment = self.env['account.payment'].create(data) 
            payment.post()
            self.concilie()
            self.payment_id=payment.id
          

                  
        

      
    def post(self):
        for rec in self:
            
            str_data = rec.data_text.replace("\'", "\"")
            account_move = json.loads(str_data)
            payment_method = account_move['payment_method']
            communication = account_move['communication']
            account_move.pop('communication')
            account_move.pop('payment_method')
            move_id = rec.env['account.move'].search([('name','=',account_move['name'])],limit=1)
            message =""
            if not move_id:
                id_new =rec.env['account.move'].create(account_move)
                id_new.post()
                rec.move_id=id_new.id
                rec.journal_id = payment_method
                rec.communication = communication
                self.payment_api()
                message += "the invoice %s was successfully created"%(id_new.name)
                rec.succes = True
            else:
                account_move.pop('invoice_line_ids')
                upd=move_id.write(account_move)  
                message += "the invoice  was successfully update"
            return message
           
            
  