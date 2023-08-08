# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date, time
from lxml import etree, objectify


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

    def send_invoice(self):

        config_parameter = self.env['ir.config_parameter']

        url = config_parameter.search(
            [('key', '=', 'URL_COMPROBANTE')]).value
        method = config_parameter.search(
            [('key', '=', 'COMPROBANTE_PAGO')]).value

        dict = self.build_dict_send_invoice()

        trama = self.get_trama_Cpe_Pago(dict, method)

        # print('*************************************')
        # print('*************************************')
        # print(trama)
        # print('*************************************')
        # print('*************************************')

        try:
            respuesta = self.get_respuesta_zeep(url, method, trama)
        except:
            self.update_state_sunat(self.id, ESTADOS_ENVIO_SUNAT['POR_ENVIAR'], _(
                'No se puedo realizar la comunicación con el Sistema Ebis. - '))
            return self.env['mensaje.emergente'].get_mensaje('WebServiceError')

        # if respuesta == None:
        #    return self.env['mensaje.emergente'].get_mensaje('Ebis no delvolvio respuesta')

        self.update_state_sunat(self.id, ESTADOS_ENVIO_SUNAT['ENVIADO'])
        return self.recibir_comprobante_pago_respuesta(respuesta)

    def update_state_sunat(self, id_comprobante, estado_final, descripcion_detallada=None):

        obj_estado_inicial = self.search(
            [('id', '=', id_comprobante)]).shipping_status_sunat
        obj_estado_final = self.env['peb.shipping.status.sunat'].search(
            [('code', '=', estado_final)])

        values = {}
        values['invoice_id'] = id_comprobante
        values['fecha'] = datetime.now().strftime('%Y-%m-%d')

        if obj_estado_final and obj_estado_inicial.id:
            values['estado_ini'] = obj_estado_inicial.name

        values['descripcion'] = obj_estado_final.description
        values['estado_fin'] = obj_estado_final.name

        if descripcion_detallada != None:
            values['descripcion_detallada'] = descripcion_detallada

        # Se registran los datos en la tabla de logs
        self.env['logs.comprobante'].create(values)

        obj_comprobante = self.search([('id', '=', id_comprobante)])
        # estado_final})
        obj_comprobante.write({'shipping_status_sunat': obj_estado_final.id})

    def button_list_logs(self):
        """
                Método que abre una nueva ventana que contiene 
                los LOGS de un documento
        """
        mod_obj = self.env['ir.model.data']
        # act_obj = self.pool.get('ir.actions.act_window')

        view_ref = mod_obj.check_object_reference('electronic_invoice', 'log_tree_view')
        view_id = view_ref and view_ref[1] or False

        id_activo = self.id

        logs_ids = []
        for so in self.env['logs.comprobante'].search([('invoice_id', '=', id_activo)]):
            logs_ids += [so.id]
        domain = "[('id','in',[" + ','.join(map(str, logs_ids)) + "])]"

        return {
            'type': 'ir.actions.act_window',
            'name': "Listado Logs",
            'view_mode': 'tree',
            'view_id': view_id,
            'res_model': 'logs.comprobante',
            'target': 'new',
            'domain': domain,
            'context': {}
        }

    def recibir_comprobante_pago_respuesta(self, rpta):
        """
                Método que procesa la respuesta obtenida 
                al realizar una petición y 
                muestra los datos procesadsos. (str)
        """
        mod_obj = self.env['ir.model.data']
        view_ref = mod_obj.check_object_reference('electronic_invoice', 'recibir_comprobante_pago_respuesta_view')
        view_id = view_ref and view_ref[1] or False
        
        if rpta:

            rpta_obj_xml = objectify.fromstring(rpta.encode('utf-8'))

            codigo_estado = self.get_tag_text(rpta_obj_xml, TAGS['COD_EST']) or ''
            observaciones = self.get_tag_text(rpta_obj_xml, TAGS['OBS']) or ''
            descripcion_estado = self.get_tag_text(rpta_obj_xml, TAGS['DESC_EST']) or ''

            if codigo_estado == INDICADOR_RESULTADO['INFO']:
                self.update_state_sunat(
                    self.id, ESTADOS_ENVIO_SUNAT['ACEPTADO_EBIS'], observaciones)
                # si esta en aceptado debe obtener los archivos como el pdf
                self.get_invoice_ebis()
                #
            elif codigo_estado == INDICADOR_RESULTADO['ERROR']:
                self.update_state_sunat(
                    self.id, ESTADOS_ENVIO_SUNAT['RECHAZADO_EBIS'], observaciones)

            
        else:
            observaciones = 'Por Enviar'
            descripcion_estado = 'El Comprobante no puedo ser enviado a EBIS'
            self.update_state_sunat(
                    self.id, ESTADOS_ENVIO_SUNAT['POR_ENVIAR'], observaciones)

        domain = "[]"
        return {
            'type': 'ir.actions.act_window',
            'name': "Comprobante de Pago Respuesta",
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'recibir.comprobante.pago.respuesta',
            'view_id': False,
            'views': [(view_id, 'form')],
            'target': 'new',
            'nodestroy': True,
            'domain': domain,
            'context': {
                'indicadorResultado': descripcion_estado,
                'mensaje': observaciones,
            }
        }
    
    def get_tag_text(self, resp, tag):
        content = False
        for child in resp.iterchildren():
            if (not content) :
                if(child.countchildren() > 0) :
                    content = self.get_tag_text(child, tag)
                else :
                    if child.tag == tag:
                        content = child.text
        return content
