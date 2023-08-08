# -*- coding: utf-8 -*-

from odoo.osv import expression
from odoo import fields, models,api
from odoo import api
from odoo.tools.translate import _
import re
from lxml import etree, objectify
from .commons import *
from .except_error import WebServiceError
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

from odoo.osv.expression import get_unaccent_wrapper

class res_partner(models.Model):
    _name="res.partner"
    _inherit="res.partner"
    
    taxpayer_ruc_state = fields.Selection(string='Estado de Contribuyente', selection=[('activo', 'Activo'), ('sustemporal', 'Suspencion temporal'),
                                                                 ('bprovicional', 'Baja Provicional'),('bdefinitiva', 'Baja definitiva'),
                                                                 ('bprovoficio', 'Baja provisional de oficio'),('bdoficio', 'Baja definitiva de oficio')],default=False,store=True)
       
    taxpayer_ruc_condition = fields.Selection(string='Condicion de Contribuyente', selection=[('habido', 'HABIDO'), ('nohabido', 'NO HABIDO')],default=False,store=True)
    

    def obtener_ubigeo(self, ubigeo):
        if len(ubigeo)==6:
            dep = ubigeo[:2]
            prov = ubigeo[:4]
            dist = ubigeo
            departento_obj = self.env['res.country.state'].search([('code','=',dep),('country_id.code','=','PE')]) or False
            provincia_obj = self.env['res.city'].search([('l10n_pe_code','=',prov)]) or False
            distrito_obj = self.env['l10n_pe.res.city.district'].search([('code','=',dist)]) or False
            return departento_obj, provincia_obj, distrito_obj

    def asignar_datos(self, values):
        self.taxpayer_ruc_state = values.get('taxpayer_state')
        self.taxpayer_ruc_condition = values.get('taxpayer_condition')
        self.name = values['nombres']
        self.names = values['nombres']
        self.street = values['street']
        if values.get('departamento') and values.get('provincia') and values.get('distrito'):
            self.state_id = values['departamento']
            self.city_id = values['provincia']
            self.l10n_pe_district = values['distrito']

    def obtener_datos(self, datos):
        values = {}
        values['nombres'] = datos.find(TAGS_PADRON_RESPUESTA['NOMBRE']).text or False
        taxpayer_state = datos.find(TAGS_PADRON_RESPUESTA['ESTADO']).text or False
        taxpayer_condition = datos.find(TAGS_PADRON_RESPUESTA['COND_DOMIC']).text or False
        direc_fisc = ""
        
        avenid = datos.find(TAGS_PADRON_RESPUESTA['TIPO_VIA']).text
        if avenid != '-':
            direc_fisc = direc_fisc + avenid
            
        nom_via = datos.find(TAGS_PADRON_RESPUESTA['NOMB_VIA']).text
        if nom_via != '-':
            direc_fisc = direc_fisc + ' ' + nom_via

        numero = datos.find(TAGS_PADRON_RESPUESTA['NUMERO']).text
        if numero != '-':
            direc_fisc = direc_fisc + ' NRO. ' + numero
        
        kilometro = datos.find(TAGS_PADRON_RESPUESTA['KM']).text
        if kilometro != '-':
            direc_fisc = direc_fisc + ' KM. ' + kilometro
        
        departamento = datos.find(TAGS_PADRON_RESPUESTA['DEPARTAMENTO']).text
        if departamento != '-':
            direc_fisc = direc_fisc + ' DPTO. ' + departamento
            
        interior = datos.find(TAGS_PADRON_RESPUESTA['INTERIOR']).text
        if interior != '-':
            direc_fisc = direc_fisc + ' INT. ' + interior

        manzana = datos.find(TAGS_PADRON_RESPUESTA['MANZANA']).text
        if manzana != '-':
            direc_fisc = direc_fisc + ' MZ. ' + manzana
            
        lote = datos.find(TAGS_PADRON_RESPUESTA['LOTE']).text or ''
        if lote != '-':
            direc_fisc = direc_fisc + ' LOTE. '+ lote
            
        cod_zona = datos.find(TAGS_PADRON_RESPUESTA['COD_ZONA']).text
        tipo_zona = datos.find(TAGS_PADRON_RESPUESTA['TIPO_ZONA']).text
        if cod_zona.find('-') == -1:
            direc_fisc = direc_fisc + ' ' +cod_zona
        if tipo_zona.find('-') == -1:
            direc_fisc = direc_fisc + ' ' + tipo_zona
            
        values['street'] = direc_fisc
        for vals in datos.findall(TAGS_PADRON_RESPUESTA['UBIGEO_TAG']):
            ubigeo = vals.find(TAGS_PADRON_RESPUESTA['COD_UBIGEO']).text or False
            if ubigeo:
                values['departamento'], values['provincia'], values['distrito'] = self.obtener_ubigeo(ubigeo)
            
        estado_contribuyente_dict = {
        'activo' : 'ACTIVO',
        'sustemporal' : 'SUSPENSION TEMPORAL',
        'bprovicional' : 'BAJA PROVISIONAL',
        'bdefinitiva' : 'BAJA DEFINITIVA',
        'bprovoficio' : 'BAJA PROVISIONAL DE OFICIO',
        'bdoficio' : 'BAJA DEFINITIVA DE OFICIO',
        }   
        
        condicion_contribuyente_dict = {
            'habido' : 'HABIDO',
            'nohabido' : 'NO HABIDO',
        }
        
        for key, value in estado_contribuyente_dict.items():
            if taxpayer_state == value:
                values['taxpayer_state'] = key
        
        for key, value in condicion_contribuyente_dict.items():
            if taxpayer_condition == value:
                values['taxpayer_condition'] = key
        
        return values

    def process_response(self, response):
        response = objectify.fromstring(response.encode('utf-8'))
        cod_error = get_tag_text(response, TAGS_PADRON_RESPUESTA['COD_ERROR']) or False
        if VALUES['EXITO'] == cod_error:
            for values in response.findall(TAGS_PADRON_RESPUESTA['LST_EMPR']):
                return self.obtener_datos(values)
        elif VALUES['ERROR'] == cod_error:
            raise Warning('Padrón Reducido', 'El RUC digitado no se encontró en la base de datos de Padrón Reducido de SUNAT.')
        else:
            msg = get_tag_text(response, TAGS_PADRON_RESPUESTA['DESCRIPCION_ERROR']) or ''
            raise except_orm('Padrón Reducido', 'Padrón Reducido retorno el siguiente error: [Código Error:'+cod_error+']-[Mensaje:'+msg+']')

    def construir_trama_consulta_padron(self, ruc, metodo):
        trama_consulta = etree.Element(metodo)
        valida_y_crea(trama_consulta, WS_PADRON['TIPO_CONSULTA'] , 'RUC', True)
        valida_y_crea(trama_consulta, WS_PADRON['RUC'] , ruc, True)
        return etree.tostring(trama_consulta, pretty_print=True)
    
    def consulta_padron_ebis(self, ruc):
        url = self.env['ir.config_parameter'].search([('key', '=', WS_PADRON['URL_NOMBRE'])]).value
        metodo = self.env['ir.config_parameter'].search([('key', '=', WS_PADRON['NOMBRE_METODO_PADRON'])]).value
        trama = self.construir_trama_consulta_padron(ruc, WS_PADRON['CUERPO_TRAMA_PADRON'])
        return get_respuesta_zeep(url, metodo, trama)

    @api.onchange('vat') #Campo 'vat' equivale a RUC
    def _onchange_vat(self):
        is_active_sunat = self.env['ir.config_parameter'].sudo().get_param('pattern_sunat.active_pattern_sunat')
        if is_active_sunat:
            if self.l10n_latam_identification_type_id and self.l10n_latam_identification_type_id.l10n_pe_vat_code == '6' and self.vat:
                self.validate_ruc(self.vat)
                response = None
                try:
                    response = self.consulta_padron_ebis(self.vat)
                except WebServiceError as e:
                    pass

                if response:
                    self.asignar_datos(self.process_response(response))

            elif self.l10n_latam_identification_type_id and self.l10n_latam_identification_type_id.l10n_pe_vat_code == '1' and self.vat:
                self.is_numero(self.vat)
