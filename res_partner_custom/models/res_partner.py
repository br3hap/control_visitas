# -*- coding: utf-8 -*-

from odoo.osv import expression
from odoo import fields, models,api
from odoo import api
from odoo.tools.translate import _
import re
from lxml import etree, objectify
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

from odoo.osv.expression import get_unaccent_wrapper

class res_partner(models.Model):
    _inherit="res.partner"

    ubigeo_required = fields.Char('Ubigeo Requerido', compute='_compute_required_ubigeo')

    @api.onchange('country_id')
    def _onchange_country(self):
        print('')
        # country = self.country_id or self.company_id.country_id or self.env.company.country_id
        # self.l10n_latam_identification_type_id = self.env['l10n_latam.identification.type'].search(
        #    [('country_id', '=', country.id), ('is_vat', '=', True)]) or self.env.ref('l10n_latam_base.it_vat', raise_if_not_found=False)

    @api.depends('l10n_latam_identification_type_id')
    def _compute_required_ubigeo(self):
        identificacion = self.l10n_latam_identification_type_id
        if identificacion:
            self.ubigeo_required = 'S' if identificacion.l10n_pe_vat_code != '0' else 'N'
        else:
            self.ubigeo_required = 'S'

    def validate_ruc(self, ruc):
        patternRuc="^[0-9]{11}$"
        sum=0
        count=10
        multiples=[5,4,3,2,7,6,5,4,3,2]
        if ruc:  
            if re.match(patternRuc,ruc):
                band=False
                n=int(ruc)//10
                while count>0:
                    sum=sum+(n%10)*multiples[count-1]
                    n=n//10
                    count=count-1
                val=11-sum%11
                last_digit=int(ruc)%10
                if val==10:
                    if(last_digit==0):
                        band=True
                else:
                    if val==11:
                        if(last_digit==1):
                            band=True
                    else:
                        if val==(last_digit):
                            band=True
                if band==False:                    
                    raise ValidationError(_("The RUC entered is invalid."))
            else:
                raise ValidationError(_("The RUC it's an 11 digit numerical value."))                

    @api.model
    def is_numero(self,dni):
        patternDni="^[0-9]{8}$"        
        
        if re.match(patternDni,dni)==None:           
            raise ValidationError(_("The DNI it's an 8 digit numerical value."))
  
    @api.onchange('names','last_name')
    def _onchange_name(self):
        is_company = self.is_company
        if is_company:
            nomb = self.names or ''
            nomb = self.remove_accent_mark(nomb)
            self.names = nomb
            self.name = self.names
        else:
            nomb = self.names or ''
            nomb = self.remove_accent_mark(nomb)
            self.names = nomb
            
            ape = self.last_name or ''
            ape = self.remove_accent_mark(ape)
            self.last_name = ape
            
            self.name = (nomb + ' ' + ape).strip()

    @api.onchange('is_company')
    def _onchange_is_company(self):
        if self.is_company:
            self.l10n_latam_identification_type_id = self.env['l10n_latam.identification.type'].search([('id','=',1)]) or None
        else:
            self.l10n_latam_identification_type_id = self.env['l10n_latam.identification.type'].search([('id','=',4)]) or None

    @api.onchange('vat') #Campo 'vat' equivale a RUC
    def _onchange_vat(self):
        if self.l10n_latam_identification_type_id and self.l10n_latam_identification_type_id.l10n_pe_vat_code == '6' and self.vat:
            self.validate_ruc(self.vat)
        elif self.l10n_latam_identification_type_id and self.l10n_latam_identification_type_id.l10n_pe_vat_code == '1' and self.vat:
            self.is_numero(self.vat)

    def remove_accent_mark(self,txt):
        #reemplazando las tildes de letras minusculas por su equivalente sin tilde
        txt = txt.replace(u'\xe1','a')
        txt = txt.replace(u'\xe9','e')
        txt = txt.replace(u'\xed','i')
        txt = txt.replace(u'\xf3','o')
        txt = txt.replace(u'\xfa','u')
        #reemplazando las tildes de letras mayusculas por su equivalente sin tilde
        txt = txt.replace(u'\xc1','A')
        txt = txt.replace(u'\xc9','E')
        txt = txt.replace(u'\xcd','I')
        txt = txt.replace(u'\xd3','O')
        txt = txt.replace(u'\xda','U')
        #reemplazando los espacion mayores a 1 dentro del nombre
        txt = re.sub(' +',' ',txt)
        #quitando los espacion delante y detras del nombre
        txt = txt.strip()
        #pasando el nombre a mayusculas
        txt = txt.upper()
        
        return txt

    names = fields.Char('Name')
    last_name = fields.Char('Last Name')
    birthday = fields.Date(string='Birthday', help='Birthday for a natural person or Date of Incorporation in case it is a legal person.')
    active_customer = fields.Boolean(string='Customer', default=lambda self: self.env.context.get('res_partner_search_mode')=='customer', is_default=True)
    active_supplier = fields.Boolean(string='Supplier', default=lambda self: self.env.context.get('res_partner_search_mode')=='supplier', is_default=True)
