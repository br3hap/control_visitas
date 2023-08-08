# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date, time
from lxml import etree, objectify
from odoo.exceptions import UserError, UserError
import re

comprobante_pattern = re.compile(r'^\w{4}-\d{1,8}$')


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


class account_move(models.Model):
    _inherit = 'account.move'

    def get_invoice_ebis(self):

        if self.move_type == 'out_invoice' or self.move_type == 'out_refund':
            assert len(self) == 1, 'Esta opción solo debe ser usada en un solo momento.'
            
            context = {}
            if self._context:
                context = self._context.copy()
            
            resp = self.solicitar_doc_ebis('IMPRESION')
            
            resp = objectify.fromstring(resp.encode('utf-8'))
            
            # Siempre traera el xml
            filecontent = False
            filecontent_xml = False
            extension = '.pdf'
            extension_xml = '.xml'

            filecontent_xml = self.get_tag_text(resp, TAGS['XML'])
            filecontent = self.get_tag_text(resp, TAGS['PDF'])

            if filecontent and filecontent_xml:
                
                journal_obj = self.journal_id
                company_obj = self.company_id
                company_partner_id = company_obj.partner_id
                data = {
                        'numerodocumento': company_partner_id.vat,
                        'tipo_documento': journal_obj.sunat_document_type.code,
                        'number': self.name
                }

                filename_field = self.get_pdf_filename(data)
                
                self.write({
                            'field_pdf': filename_field+extension,
                            'file_data': filecontent,
                            'field_xml': filename_field+extension_xml,
                            'file_data_xml': filecontent_xml,
                            'not_active_get_print_invoice': True
                            })
            else:
                raise UserError(_("Documento no encontrado"))	
    
    def solicitar_doc_ebis(self, tipo):
        try:
            config_parameter = self.env['ir.config_parameter']

            url = config_parameter.search(
                [('key', '=', 'URL_COMPROBANTE')]).value
            method = config_parameter.search(
                [('key', '=', 'IMPRESION')]).value

            dict = self.build_dict_print_invoice()
            
            dict['tipo_desc'] = self._context.get('tipo_desc', False)
            
            trama = self.get_trama_print_invoice(dict, method)

            respuesta = self.get_respuesta_zeep(url, method, trama)
        except:
            raise UserError(_("Error en el proceso Solicitado"))
        return respuesta

    def solicitar_txt_ebis(self, tipo):
        try:
            config_parameter = self.env['ir.config_parameter']
            method = config_parameter.search([('key', '=', tipo)]).value
            dict = self.build_dict_print_invoice()
            dict['tipo_desc'] = 'TXT'
            trama = self.get_trama_print_invoice(dict, method)
            url = config_parameter.search([('key', '=', 'URL_COMPROBANTE')]).value
            respuesta = self.get_respuesta_zeep(url, method, trama)
        except Exception as e:
            raise UserError('WebService Error',
            _("Comunicarse con el Adminstrador del Sistema - '%s'") % _(e,))
        return respuesta

    def get_pdf_filename(self, dic):
        filename = False
        
        num_doc_id_emi = dic.get('numerodocumento', False)
        tipo_doc = dic.get('tipo_documento', False) #get_tipo_doc(dic.get('journal_code', False))
        number = dic.get('number', False)
            
        serie = False
        correlativo = False
        if number and comprobante_pattern.match(number) is not None:
            serie, correlativo = number.split('-')
        
        if (num_doc_id_emi and tipo_doc and serie and correlativo) :
            filename = num_doc_id_emi + '-' + tipo_doc + '-' + serie + '-' + correlativo   
        return filename
    
class impresiones(models.TransientModel):
    _name='impresion'
    _description = 'impresion'
    file_id = fields.Binary('Impresion Temporal')
