# -*- coding: utf-8 -*-

import base64
import datetime
import logging
import hashlib
import time

from datetime import datetime
from lxml import etree, objectify
from odoo import fields, models, api,  _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone
from odoo.exceptions import UserError, UserError

ESTADOS_ENVIO_SUNAT = {
    'POR_ENVIAR': '1',
    'ENVIADO': '2',
    'ACEPTADO_EBIS': '3',
    'RECHAZADO_EBIS': '4',
    'ACEPTADO_SUNAT': '5',
    'ACEPTADO_SUNAT_OBS.': '6',
    'RECHAZADO_SUNAT': '7',
    'PARA_CORREGIR': '8',
    'EN_PROCESO_BAJA': '9',
    'BAJA_ACEPTADA': '10',
    'BAJA_RECHAZADA': '11',
}

TAGS = {
    'COD_EST': 'codigoEstado',
    'DESC_EST': 'descripcionEstado',
    'OBS': 'observaciones',
    'PDF': 'archivoBase64Pdf',
    'DOCUMENTO_ENCONTRADO': 'indicadorDocumentoEncontrado',
    'INDICADOR_PDF_GENERADO': 'indicadorPdfGenerado',
    'MENSAJE_RESPUESTA_PDF': 'mensajeRespuestaPdf',
    'MENSAJE_RESPUESTA_TXT': 'mensajeRespuestaTxt',
    'CONTENIDO_TXT': 'contenidoTxt',
    'INDICADOR_TXT_GENERADO': 'indicadorTxtGenerado',
    'XML': 'archivoBase64Xml',
    'MENSAJE_RESPUESTA_XML': 'mensajeRespuestaXml',
}


TAGS_RESULTADO_PROCESO = {
    'INDICADOR': 'indicador',
    'MSG': 'mensaje',
}

VALORES = {
    'EXITO': '1',
    'ERROR': '0',
}

INDICADOR_RESULTADO = {
    'INFO': '3',
    'ERROR': '4',
}

TAG_ELEMENTOS_ADICIONALES = {
    'NOMBRE_EBIS': 'propiedadesAdicionales',
    'CODIGO_EBIS': 'codigoPropiedadAdicional',
    'DESC_EBIS': 'descripcionPropiedadAdicional',
}

class bajas(models.Model):
    _name = 'bajas'
    _description = 'bajas'
    def button_create_send_low(self):
        if self.invoice_id:
            cpe = self.invoice_id
            company = cpe.company_id
            cod_emi = company.emisor_code
            pass_security = company.pass_security
            number = cpe.name
            cod_tipo_doc_emi =  company.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code
            num_doc_id_emi = company.partner_id.vat
            fecha_emision = self.fecha_emision.strftime('%Y-%m-%d %H:%M:%S')
            fec_emi, hora_emi = fecha_emision.split(' ')
            motivo = (self.motivo_baja).strip()
            raz_soc_emi = company.display_name

            if cpe.move_type == 'out_refund':
                tipo_documento = cpe.journal_id.sunat_document_type_related.code
            else:
                tipo_documento = cpe.journal_id.sunat_document_type.code
            
            # DNINACO, FALTABA EL DOCUMENTO RELACIONADO
            cod_doc_mod = ""
            if cpe.related_document_type:
                cod_doc_mod = cpe.related_document_type
            
            err_msg = False
            
            if (len(motivo) < 3) or (len(motivo) > 100) :
                err_msg = 'El Motivo de la Baja debe tener un tamaño mínimo de 3 caracteres y un máximo de 100 caracteres.'
                
            if (err_msg) :
                raise UserError(_(err_msg))
            else :
                if (cod_emi and number and tipo_documento and cod_tipo_doc_emi and num_doc_id_emi and fec_emi and hora_emi and motivo and raz_soc_emi) :
                    try:
                        
                        baja = self
                        
                        self.actualizar_estado_sunat(baja.id, ESTADOS_ENVIO_SUNAT['ENVIADO'])
                        
                        config_parameter = self.env['ir.config_parameter']

                        url = config_parameter.search(
                            [('key', '=', 'URL_COMPROBANTE')]).value
                        method = config_parameter.search(
                            [('key', '=', 'BAJA_COMPROBANTE')]).value
                        
                        dict = {'codigoEmisor' : cod_emi,
                            'pass_security': pass_security,
                            'number' : number,
                            'tipo_documento' : tipo_documento,
                            'cod_tipo_doc_emi' : cod_tipo_doc_emi,
                            'num_doc_id_emi' : num_doc_id_emi,
                            'fec_emi' : fec_emi,
                            'hora_emi' : hora_emi,
                            'motivo' : motivo,
                            'raz_soc_emi' : raz_soc_emi,
                            'cod_doc_mod': cod_doc_mod
                            }
                        
                        trama = cpe.get_trama_baja_cpe_pago(dict, method)
                        # print(trama)
                        respuesta = cpe.get_respuesta_zeep(url, method, trama)
                        
                        return self.recibir_comprobante_pago_respuesta(respuesta)
                    except:
                        raise UserError(_("Error en el Web Service")) 
                    
    def actualizar_estado_sunat(self, id_comprobante, estado_final, descripcion_detallada=None):

        obj_estado_inicial = self.search([('id','=',id_comprobante)]).shipping_status_sunat
        obj_estado_final = self.env['peb.shipping.status.sunat'].search([('code','=',estado_final)])
        
        values = {}
        values['baja_id'] = id_comprobante
        values['fecha'] = datetime.now().strftime('%Y-%m-%d')
        
        if obj_estado_final and obj_estado_inicial:
            values['estado_ini'] = obj_estado_inicial.name
            
        values['descripcion'] = obj_estado_final.description
        values['estado_fin'] = obj_estado_final.name
        
        if descripcion_detallada != None:
            values['descripcion_detallada'] = descripcion_detallada
        
        #Se registran los datos en la tabla de logs
        self.env['logs.baja'].create(values)
        
        obj_comprobante = self.search([('id','=',id_comprobante)])
        obj_comprobante.write({'shipping_status_sunat': obj_estado_final.id})

    '''    
    def actualizar_estado_sunat_cron(self, cr, uid, id_comprobante, estado_final, descripcion_detallada=None, context=None):
        """
            Método que actualiza el estado del comprobante,
            y registra el respectiv log de la actualización.
            :param int id_comprobante : id del comprobante
            :param int estado_final : codigo del estado final
        """
        obj_estado_inicial_id = self.search(cr, uid, [('id', '=', id_comprobante)], context=context)
        obj_estado_inicial = self.browse(cr, uid, obj_estado_inicial_id).estado_envio_sunat
        obj_estado_final_id = self.pool.get('estados.envio.sunat').search(cr, uid, [('codigo', '=', estado_final)], context=context)
        obj_estado_final = self.pool.get('estados.envio.sunat').browse(cr, uid, obj_estado_final_id, context=context)
        
        values = {}
        values['baja_id'] = id_comprobante
        values['fecha'] = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        
        if obj_estado_final and obj_estado_inicial.id:
            values['estado_ini'] = obj_estado_inicial.nombre
            
        values['descripcion'] = obj_estado_final.descripcion
        values['estado_fin'] = obj_estado_final.nombre
        
        if descripcion_detallada != None:
            values['descripcion_detallada'] = descripcion_detallada
        
        # Se registran los datos en la tabla de logs
        self.pool.get('logs.baja').create(cr, uid, values, context=context)
        
        self.write(cr, uid, id_comprobante, {'estado_envio_sunat': obj_estado_final_id[0]}, context=context)
    '''        
    def recibir_comprobante_pago_respuesta(self, rpta):
        
        # instanciamos el comporbante
        cpe = self.invoice_id

        mod_obj = self.env['ir.model.data']
        view_ref = mod_obj.check_object_reference('electronic_invoice', 'recibir_comprobante_pago_respuesta_view')
        view_id = view_ref and view_ref[1] or False
        
        rpta_obj_xml = objectify.fromstring(rpta.encode('utf-8'))
        
        codigo_estado = cpe.get_tag_text(rpta_obj_xml, TAGS['COD_EST']) or ''
        observaciones = cpe.get_tag_text(rpta_obj_xml, TAGS['OBS']) or ''
        descripcion_estado = cpe.get_tag_text(rpta_obj_xml, TAGS['DESC_EST']) or ''
        
        if codigo_estado == INDICADOR_RESULTADO['INFO']:
            self.actualizar_estado_sunat(self.id, ESTADOS_ENVIO_SUNAT['ACEPTADO_EBIS'], observaciones)
            self.env['account.move'].update_state_sunat(self.invoice_id.id, ESTADOS_ENVIO_SUNAT['EN_PROCESO_BAJA'], observaciones)
        elif codigo_estado == INDICADOR_RESULTADO['ERROR']:
            self.actualizar_estado_sunat(self.id, ESTADOS_ENVIO_SUNAT['RECHAZADO_EBIS'], observaciones)
            
        domain = "[]"
        return {
                'type': 'ir.actions.act_window',
                'name':"Comprobante de Pago Respuesta",
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'recibir.comprobante.pago.respuesta',
                'view_id': False,
                'views': [(view_id, 'form')],
                'target': 'new',
                'nodestroy': True, 
                'domain': domain,
                'context': {
                    'indicadorResultado' : descripcion_estado,
                    'mensaje' : observaciones,
                }
        }
    
    def _compute_estado_envio_sunat(self):
        self.est_sunat = self.shipping_status_sunat.code
    
    invoice_id = fields.Many2one('account.move', string="Comprobante", readonly=True, default=lambda self:self._context.get('invoice_id', False))
    
    fecha_emision = fields.Datetime('Fecha de Emisión', default=lambda self:self._context.get('fecha_hora', False), readonly=True)
    
    motivo_baja = fields.Text(string='Motivo de la baja', size=100, required=True)
    
    shipping_status_sunat = fields.Many2one('peb.shipping.status.sunat', string="Estado SUNAT", readonly=True)
    
    est_sunat = fields.Char(compute='_compute_estado_envio_sunat')
