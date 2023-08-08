# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import time
import datetime
from datetime import datetime, date, time
from odoo.exceptions import UserError, UserError
from lxml import etree, objectify

TIPOS_COMPROBANTE = {
        'FACTURA':'01',
        'BOLETA':'03',
        'NOTA_CREDITO':'07',
        'NOTA_DEBITO':'08',
        'GUIA_REMISION_REMITENTE':'09',
        'NOTA_PEDIDO':'NP',
    }

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

TAGS_CONSUL_EST_COMP = {
        'LISTA': 'listaComprobantes',
    }

TAGS_CONSUL_COMPROBANTE = {
        'NOMBRE': 'comprobante',
        'COD_ESTADO': 'codigoEstado',
        'CORRELATIVO': 'correlativo',
        'DESC_ESTADO': 'descripcionEstado',
        'OBS': 'observaciones',
        'RUC_EMI': 'rucEmisor',
        'SERIE': 'serie',
        'TIPO_COMP': 'tipoDocumento',
    }


class account_move(models.Model):
    _inherit = 'account.move'

    def consulta_respuesta_sunat(self, cod_emisor=False, inclu_boletas=False, inclu_bajas=False):
        # print(
        #     '/********** INICIO DEL CRON DEL CONSULTA DE ESTADOS DE COMPROBANTE **********/')
        # print('- EMISOR: ' + cod_emisor)
        # print('- SE INCLUYEN BOLETAS: ' + str(inclu_boletas))
        # print('- SE INCLUYEN BAJAS: ' + str(inclu_bajas))

        company_id = self.env['res.company'].search(
            [('emisor_code', '=', cod_emisor)])

        config_parameter = self.env['ir.config_parameter']

        url = config_parameter.search(
            [('key', '=', 'URL_COMPROBANTE')]).value
        method = config_parameter.search(
            [('key', '=', 'CONSULTAR_ESTADO_COMPROBANTE')]).value

        dominio = []
        dominio_guia = []

        obj_est_sunat = self.env['peb.shipping.status.sunat']

        est_ace_ebis = obj_est_sunat.search(
            [('code', '=', ESTADOS_ENVIO_SUNAT['ACEPTADO_EBIS'])])
        est_para_corregir = obj_est_sunat.search(
            [('code', '=', ESTADOS_ENVIO_SUNAT['PARA_CORREGIR'])])
        est_en_proceso_baja = obj_est_sunat.search(
            [('code', '=', ESTADOS_ENVIO_SUNAT['EN_PROCESO_BAJA'])])

        if inclu_boletas:
            dominio = [('shipping_status_sunat', 'in', est_ace_ebis.id),
                        ('company_id', '=', company_id.id)]
            
            if inclu_bajas:
                dominio = [('shipping_status_sunat', 'in', [est_ace_ebis.id, est_en_proceso_baja.id]),
                        ('company_id', '=', company_id.id)]

        else:
            boleta_id = self.env['peb.catalogue.01'].search(
                [('code', '=', TIPOS_COMPROBANTE['BOLETA'])]).ids

            journal_id = self.env['account.journal'].search(
                [('sunat_document_type', 'in', boleta_id), ('company_id', '=', company_id.id)]).ids
                
            dominio = [('journal_id', 'not in', journal_id), ('shipping_status_sunat', 'in', [
                        est_ace_ebis.id, est_para_corregir.id]), ('company_id', '=', company_id.id)]

            if inclu_bajas:
                dominio = [('journal_id', 'not in', journal_id), ('shipping_status_sunat', 'in', [
                        est_ace_ebis.id, est_para_corregir.id, est_en_proceso_baja.id]), ('company_id', '=', company_id.id)]

        dominio_guia = [('shipping_status_sunat', 'in', [est_ace_ebis.id, est_para_corregir.id]), 
                        ('company_id', '=', company_id.id)]
        
        guias = []
        print("###domain",dominio)
        comprobantes = self.search(dominio)
        print("###domain",comprobantes)
        if comprobantes:
            trama = self.contruir_trama_consulta_respuesta(cod_emisor, method, comprobantes, guias)
            # print(trama)
            respuesta = self.get_respuesta_zeep(url, method, trama)
            self.procesar_respueta_sunat(respuesta)     
        
        comprobantes = []
        guias = self.env['stock.picking'].search(dominio_guia)
        if guias:
            trama = self.contruir_trama_consulta_respuesta(cod_emisor, method, comprobantes, guias)
            # print(trama)
            respuesta = self.get_respuesta_zeep(url, method, trama)
            self.procesar_respueta_sunat(respuesta)            
               
        # print('/********** FIN DEL CRON DEL CONSULTA DE ESTADOS DE COMPROBANTE **********/')
    
    def procesar_respueta_sunat(self, rpta):
        """
            Método para procesar la respuesta SUNAT
        """

        rpta = objectify.fromstring(rpta.encode('utf-8'))

        indicador = self.get_tag_text(rpta, TAGS_RESULTADO_PROCESO['INDICADOR']) or False

        if VALORES['EXITO'] == indicador:
            for lista in rpta.findall(TAGS_CONSUL_EST_COMP['LISTA']):
                for comp in lista.findall(TAGS_CONSUL_COMPROBANTE['NOMBRE']):
                    self.actualizar_estado_comprobante(comp)
    
    def actualizar_estado_comprobante(self, cmp):
		
        serie = cmp.find(TAGS_CONSUL_COMPROBANTE['SERIE']).text
        correlativo = cmp.find(TAGS_CONSUL_COMPROBANTE['CORRELATIVO']).text
        cod_estado = cmp.find(TAGS_CONSUL_COMPROBANTE['COD_ESTADO']).text
        obs = cmp.find(TAGS_CONSUL_COMPROBANTE['OBS']).text
        ruc_emi = cmp.find(TAGS_CONSUL_COMPROBANTE['RUC_EMI']).text
        tipo_comp = cmp.find(TAGS_CONSUL_COMPROBANTE['TIPO_COMP']).text

        company_id = self.env['res.company'].search([('partner_id.vat', '=', ruc_emi)])
        number = serie + '-' + correlativo

        if tipo_comp == TIPOS_COMPROBANTE['GUIA_REMISION_REMITENTE']:
            obj_comp = self.env['stock.picking'].search([('number_sunat', '=', number), ('company_id', '=', company_id.id)])
			#obj_comp = self.pool.get('stock.picking').browse(cr, uid, comp_id, context={})

        else:
            tipo = self.obtener_tipo_comprobante(tipo_comp)
            obj_comp = self.search([('move_type', '=', tipo), ('name', '=', number), ('company_id', '=', company_id.id)])

        if obj_comp.id and cod_estado:
            if obj_comp.shipping_status_sunat.code != cod_estado:
                if cod_estado == ESTADOS_ENVIO_SUNAT['BAJA_ACEPTADA']:
                    # ponemos en borrador las anuladas
                    obj_comp.button_draft()
                    # proceedemos a cancelar el comprobante
                    obj_comp.button_cancel()

                
                self.actualizar_estado_sunat_cron(tipo_comp, obj_comp, cod_estado, obs, company_id)


    def obtener_tipo_comprobante(self, tipo_comp):
        out_invoice_list = ['01', '03', '08']
        out_refund_list = ['07']
        
        tipo = False
        if tipo_comp in out_invoice_list:
            tipo = 'out_invoice'
        elif tipo_comp in out_refund_list:
            tipo = 'out_refund'
        return tipo
    
    def actualizar_estado_sunat_cron(self, tipo_comp, id_comprobante, estado_final, descripcion_detallada, company_id):
		
        values = {}

        if tipo_comp == TIPOS_COMPROBANTE['GUIA_REMISION_REMITENTE']:
            obj_estado_inicial = self.env['stock.picking'].search([('id', '=', id_comprobante.id), ('company_id', '=', company_id.id)])
            values['guia_remision_id'] = id_comprobante.id
            log_model = 'logs.guia.remision'

        else:
            obj_estado_inicial = self.search([('id', '=', id_comprobante.id), ('company_id', '=', company_id.id)])
            values['invoice_id'] = id_comprobante.id
            log_model = 'logs.comprobante'


        obj_estado_final = self.env['peb.shipping.status.sunat'].search([('code', '=', estado_final)])

        values['fecha'] = datetime.now().strftime('%Y-%m-%d')

        if obj_estado_final and obj_estado_inicial.id:
            values['estado_ini'] = obj_estado_inicial.name
            
        values['descripcion'] = obj_estado_final.description
        values['estado_fin'] = obj_estado_final.name

        if descripcion_detallada != None:
            values['descripcion_detallada'] = descripcion_detallada

        # Se registran los datos en la tabla de logs
        self.env[log_model].create(values)

        id_comprobante.write({'shipping_status_sunat': obj_estado_final.id})
