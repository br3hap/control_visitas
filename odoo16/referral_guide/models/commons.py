# -*- coding: utf-8 -*-
##############################################################################
#
#    HENRY GUIJA FLORES
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import base64
import datetime
import logging
import hashlib
import time
import re

from datetime import datetime
from lxml import etree
#from openerp.exceptions import UserError
from odoo.exceptions import UserError
#from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

#from urllib2 import HTTPSHandler
import ssl

from requests import Session
from zeep import Client as ClientZepp
from zeep.transports import Transport

#from openerp import _, tools
from odoo import _, tools
#from except_error import WebServiceError
from .except_error import WebServiceError
from xml.sax.saxutils import escape
from docutils.nodes import author
from _ast import Not

_logger = logging.getLogger(__name__)

comprobante_pattern = re.compile(r'^\w{4}-\d{1,8}$')

WS = {
    'URL_COMPROBANTE':'URL_COMPROBANTE',
    'CONSULTAR_ESTADO_COMPROBANTE':'CONSULTAR_ESTADO_COMPROBANTE',
    'IMPRESION':'IMPRESION',
    'BAJA_COMPROBANTE':'BAJA_COMPROBANTE',
    'COMPROBANTE_PAGO':'COMPROBANTE_PAGO',
    'GUIA_REMISION':'GUIA_REMISION',
    }

ESTADOS_ENVIO_SUNAT = {
        'POR_ENVIAR' : '1',
        'ENVIADO' : '2',
        'ACEPTADO_EBIS' :'3',
        'RECHAZADO_EBIS' : '4',
        'ACEPTADO_SUNAT' : '5',
        'ACEPTADO_SUNAT_OBS.' : '6',
        'RECHAZADO_SUNAT' : '7',
        'PARA_CORREGIR' : '8',
        'EN_PROCESO_BAJA' : '9',
        'BAJA_ACEPTADA' : '10',
        'BAJA_RECHAZADA':'11',
    }

TIPOS_COMPROBANTE = {
        'FACTURA':'01',
        'BOLETA':'03',
        'NOTA_CREDITO':'07',
        'NOTA_DEBITO':'08',
        'GUIA_REMISION_REMITENTE':'09',
        'NOTA_PEDIDO':'NP',
    }

TAGS = {
        'COD_EST' : 'codigoEstado',
        'DESC_EST' : 'descripcionEstado',
        'OBS' : 'observaciones',
        'PDF' : 'archivoBase64Pdf',
        'DOCUMENTO_ENCONTRADO':'indicadorDocumentoEncontrado',
        'INDICADOR_PDF_GENERADO':'indicadorPdfGenerado',
        'MENSAJE_RESPUESTA_PDF':'mensajeRespuestaPdf',
        'MENSAJE_RESPUESTA_TXT':'mensajeRespuestaTxt',
        'CONTENIDO_TXT':'contenidoTxt',
        'INDICADOR_TXT_GENERADO':'indicadorTxtGenerado',
        'XML' : 'archivoBase64Xml',
        'MENSAJE_RESPUESTA_XML' : 'mensajeRespuestaXml',
    }

TAGS_CONSUL_EST_COMP = {
        'LISTA':'listaComprobantes',
    }

TAGS_CONSUL_COMPROBANTE = {
        'NOMBRE':'comprobante',
        'COD_ESTADO':'codigoEstado',
        'CORRELATIVO':'correlativo',
        'DESC_ESTADO':'descripcionEstado',
        'OBS':'observaciones',
        'RUC_EMI':'rucEmisor',
        'SERIE':'serie',
        'TIPO_COMP':'tipoDocumento',
    }

TAGS_RESULTADO_PROCESO = {
        'INDICADOR':'indicador',
        'MSG':'mensaje',
    }

VALORES = {
        'EXITO':'1',
        'ERROR':'0',
    }

INDICADOR_RESULTADO = {
        'INFO' : '3',
        'ERROR' : '4',
    }

ESTR_VARIABLE = {
        'ESTR_NOMBRE': 'estructuraVariable',
        'LISTADO': 'listadoDeEstructuras',
        'NOMBRE': 'nombre',
        'VALOR': 'valor',
    }
     
VALIDA_GUIA = {
        'VALIDO':'1',
        'VALIDO_SIN_DOC_REL': '2',
    }

PRODUCTO_TIPO = {
        'ALMACENABLE':u'product',
        'CONSUMIBLE':u'consu',
        'SERVICIO':u'service',
    }

ELEMENTOS_ADICIONALES = {
    'AMAZONIA': {
        'BIEN_CODIGO':'2001',
        'SERCICO_CODIGO':'2002',
        },
    }

TAG_ELEMENTOS_ADICIONALES = {
    'NOMBRE_EBIS':'propiedadesAdicionales',
    'CODIGO_EBIS':'codigoPropiedadAdicional',
    'DESC_EBIS':'descripcionPropiedadAdicional',
    }

def get_respuesta_zeep(url, metodo, trama):
    """
        Método que consume un servicio .wsdl
        
        :param str url: direccion donde se encuentra expuesto el método
        :param str metodo: nombre del metodo a consumir
        :param str trama: data que consume el metodo
        :returns: 
    """
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('zeep.transports').setLevel(logging.DEBUG)
    #logging.getLogger('zeep.client').setLevel(logging.DEBUG)
    #logging.getLogger('suds.transport').setLevel(logging.DEBUG)
    #logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
    #logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)
    try:
        session = Session()
        session.verify = False
        transport = Transport(session=session)
        cliente = ClientZepp(url, transport=transport)
        return getattr(cliente.service, metodo)(trama)
    except Exception as e:
        raise WebServiceError(e)

def get_tag_text(resp, tag):
    content = False
    for child in resp.iterchildren():
        if (not content) :
            if(child.countchildren() > 0) :
                content = get_tag_text(child, tag)
            else :
                if child.tag == tag:
                    content = child.text
    return content
    '''content = False
    for child in resp.iterchildren():
        if child.tag == tag:
            return child.text
        if child.countchildren() > 0:
            return get_tag_text(child, tag)'''
    
"""
# Función para obtener el tipo de comprobante SUNAT
def get_tipo_doc(codigo):
    if (codigo == TIPOS_COMPROBANTE['BOLETA']) :
        return '03'
    elif (codigo == TIPOS_COMPROBANTE['FACTURA']) :
        return '01'
    elif (codigo == TIPOS_COMPROBANTE['NOTA_CREDITO_CLIENTE_FACTURA'] or codigo == TIPOS_COMPROBANTE['NOTA_CREDITO_CLIENTE_BOLETA']) :
        return '07'
    elif (codigo == TIPOS_COMPROBANTE['NOTA_DEBITO']) :
        return '08'
"""

# Función que valida que el dato exista y crea el tag con el texto mandado como parametro
def valida_y_crea(obj, tag, txt, Sub):
    
    if (isinstance(txt, float)) :
        txt = str('%.2f' % txt)
        if (txt == 'False'):
            txt = False
        
    if (isinstance(txt, int)) :
        txt = str(txt)
        if (txt == 'False'):
            txt = False
        
    if (txt) :
        child = etree.Element(tag)
        child.text = txt
    
        if (Sub) :
            obj.append(child)
        else :
            return child

def get_pdf_filename(dic):
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

# Función para obtener la cabecera
def gen_header(obj, codigoEmisor, metodo,modelo):
    #SE MODIFICO PARA QUE TRAIGA LO QUE SE CONFIGURO EN LA COMPANIA
    psw = modelo.company_id.pass_security
    
    metodo = metodo + 'Request'
    
    fecha_transac = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    
    token = get_token(codigoEmisor, fecha_transac, metodo, psw)
    
    header = etree.Element("header")
    
    valida_y_crea(header, 'fechaTransaccion', fecha_transac, True)
    valida_y_crea(header, 'idEmisor', codigoEmisor, True)
    valida_y_crea(header, 'token', token, True)
    valida_y_crea(header, 'transaccion', metodo, True)
    
    obj.append(header)

def get_token(cod_emisor, fecha_transac, metodo, psw):
    token = False
    if (cod_emisor and fecha_transac and metodo and psw) :
        cadena = cod_emisor + fecha_transac + metodo + psw
        m = hashlib.sha1()
        m.update(cadena.encode())
        token = base64.b64encode(m.digest())
    return token

def gen_cpePagElectKey(obj, serie, correlativo, tipoDoc, numDocIdEmi,dict=None): #Jeefrey
    cpePagoElectVentaKey = etree.Element("identificador")
    
    valida_y_crea(cpePagoElectVentaKey, 'codigoTipoDocumento', tipoDoc, True)
    valida_y_crea(cpePagoElectVentaKey, 'numeroCorrelativo', correlativo, True)
    valida_y_crea(cpePagoElectVentaKey, 'numeroDocumentoIdentificacionEmisor', numDocIdEmi, True)
    valida_y_crea(cpePagoElectVentaKey, 'serie', serie, True)
#Jeefrey: inicio  
    if dict:     
        if tipoDoc=='01':
            valida_y_crea(cpePagoElectVentaKey, 'letraIniTipoDocFisico', 'F', True) 
        if tipoDoc=='03':
            valida_y_crea(cpePagoElectVentaKey, 'letraIniTipoDocFisico', 'B', True)
        
        if tipoDoc=='07' or tipoDoc=='08':                               
            if dict['cod_doc_mod']=='01':
                valida_y_crea(cpePagoElectVentaKey, 'letraIniTipoDocFisico', 'F', True) 
            if dict['cod_doc_mod']== '03':
                valida_y_crea(cpePagoElectVentaKey, 'letraIniTipoDocFisico', 'B', True)
        
        valida_y_crea(cpePagoElectVentaKey, 'tipoEmision', 'FIS', True)
#fin          
    obj.append(cpePagoElectVentaKey)


#DNINACO SE AGREGO MODELO=FALSE, ESTE ALVERGARA DATOS PARA OBTENER LA PASS SECURITY
def get_trama_imprimir_cpe_pago(dict, metodo,modelo=False):
    cod_emi = dict.get('codigo_emisor', False)
    imp_cpe_pago_pet = etree.Element('wsImprimirComprobantePagoPeticion')
    valida_y_crea(imp_cpe_pago_pet, 'codigoEmisor', cod_emi, True)
    
    # para obtener la serie y correlativo
    number = dict.get('number', False)
    serie = False
    correlativo = False
    if number and comprobante_pattern.match(number) is not None:
        serie, correlativo = number.split('-')
    
    gen_header(imp_cpe_pago_pet, cod_emi, metodo,modelo)
    
    tipo_doc = dict.get('tipo_documento', False) #get_tipo_doc(dict.get('journal_code', False))
    num_doc_id_emi = dict.get('numerodocumento', False)
    
    gen_cpePagElectKey(imp_cpe_pago_pet, serie, correlativo, tipo_doc, num_doc_id_emi)
    valida_y_crea(imp_cpe_pago_pet, 'fechaEmision', dict.get('date_invoice', False), True)
    tipo_desc = dict.get('tipo_desc', False)
        
    if tipo_desc and tipo_desc == u'TXT':
        valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionTxt', 'S', True)
        valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionXml', 'N', True)
        valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionPdf', 'N', True)
    elif tipo_desc and tipo_desc == u'XML':
        valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionTxt', 'N', True)
        valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionXml', 'S', True)
        valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionPdf', 'N', True)
    else:
        valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionTxt', 'N', True)
        valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionXml', 'S', True)
        valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionPdf', 'S', True)
    
    valida_y_crea(imp_cpe_pago_pet, 'indicadorTipoDocumento', 'V', True)
    return etree.tostring(imp_cpe_pago_pet, pretty_print=True)



# Función para obtener los datos de dirección y ubigeo
def get_dir(obj, tipo, dict):
    if (tipo == 'emi') :
        dir = etree.SubElement(obj, 'direccionEmisor')
        valida_y_crea(dir, 'codigoSunatAnexo', dict.get('codigoAnexo', False), True)
    else :
        dir = etree.SubElement(obj, 'direccionAdquiriente')
    
    valida_y_crea(dir, 'codigoPais', dict.get(tipo + '_pais_cod', False), True)
    
    cod_dept = dict.get(tipo + '_dept_cod', False)
    cod_prov = dict.get(tipo + 'dist_cod', False)
    cod_dist = dict.get(tipo + '_prov_name', False)
    
    if (cod_dept and cod_prov and cod_dist) :
        valida_y_crea(dir, 'codigoUbigeo', cod_dept + cod_prov + cod_dist, True)
    
    valida_y_crea(dir, 'departamento', dict.get(tipo + '_dept_name', False), True)
    valida_y_crea(dir, 'direccionDetallada', dict.get(tipo + '_dir', False), True)
    valida_y_crea(dir, 'distrito', dict.get(tipo + '_dist_name', False), True)
    valida_y_crea(dir, 'provincia', dict.get(tipo + '_prov_name', False), True)

def get_doc_modify(obj, dict):
    tipo_doc = dict.get('cod_doc_mod', False)  # get_tipo_doc(dict.get('cod_doc_mod', False))
    if tipo_doc:
        doc_mod = etree.SubElement(obj, 'documentosModificados')

        valida_y_crea(doc_mod, 'codigoTipoDocumento', tipo_doc, True)
        valida_y_crea(doc_mod, 'fechaEmision', dict.get('fec_emi_doc_mod', False), True)
        valida_y_crea(doc_mod, 'importeTotal', dict.get('imp_tot_doc_mod', False), True)

        # para obtener la serie y correlativo
        number = dict.get('numb_doc_mod', False)
        serie = False
        correlativo = False
        if number and comprobante_pattern.match(number) is not None:
            serie, correlativo = number.split('-')

        valida_y_crea(doc_mod, 'serie', serie, True)
        valida_y_crea(doc_mod, 'numeroCorrelativo', correlativo, True)

# Función para obtener los datos de Impuestos Globales
def get_taxes(obj, tipo, dict):
    
    if tipo != 'Global':
        if (tipo == 'Global') :
            tipos = tipo + 'es'
        else :
            tipos = tipo + 's'
        
        imp = etree.SubElement(obj, 'impuestos' + tipos)
        
        valida_y_crea(imp, 'codigoImpuesto' + tipo, dict.get('cod_imp', False), True)
        
        #DNINACO CUANDO ES GRATUITA ESTE TAAG NO DEBE ENVIARSE
        if dict.get('gratuito', False)==False and dict.get('cod_imp', False)!="7152":
            valida_y_crea(imp, 'codigoInternacionalImpuesto', dict.get('cod_int_imp', False), True)
        
        if (tipo == 'Unitario') :
            #DNINACO SI ES LA VENTA O REGALO DE BOLSA NO DEBE ENVIARSE ESTE TAG
            if dict.get('cod_imp', False)!="7152":
                valida_y_crea(imp, 'codigoTipoAfectacionIgv', dict.get('cod_tipo_afect_igv', False), True)
            
            '''DNINACO, AGREGANDOO TAGS EXTRAS '''
            #DNINACO SII ES GRATUITO DEBE SETEARSE EL VALOR DE REFERENCIA
            if dict.get('gratuito', False):
                valida_y_crea(imp, 'montoBaseImpuesto', dict.get('imp_gratuito', False), True)
            elif dict.get('cod_imp', False) == "7152":
                # DNINACO SE ENVIA EL TAG MONTO UNITARIO
                valida_y_crea(imp, 'montoUnitario', dict.get('importe_afectacion_bolsa', False), True)
            else:
                valida_y_crea(imp, 'montoBaseImpuesto', dict.get('montoBaseImpuesto', False), True)
    
            #DNINACO CUANDO ES GRATUITA ESTE TAAG NO DEBE ENVIARSE
            if dict.get('gratuito', False) == False and dict.get('cod_imp', False)!="7152":
                valida_y_crea(imp, 'tasaImpuesto', dict.get('tasaImpuesto', False), True)
        
        #DNINACO CUANDO ES GRATUITA ESTE TAAG NO DEBE ENVIARSE
        if dict.get('gratuito', False)==False and dict.get('cod_imp', False)!="7152":
            valida_y_crea(imp, 'nombreImpuesto' + tipo, dict.get('nomb_imp', False), True)
        
        if (tipo == 'Global') :
            valida_y_crea(imp, 'sumatoriaImpuesto' + tipo, dict.get('sum_tot_imp', False), True)
            valida_y_crea(imp, 'sumatoriaSubtotalImpuesto' + tipo, dict.get('sum_subtot_imp', False), True)
        else :
            #DNINACO SII ES GRATUITO DEBE SETEARSE EL VALOR DE REFERENCIA
            if dict.get('gratuito', False):
                valida_y_crea(imp, 'montoTotalImpuesto' + tipo, dict.get('imp_trib_gratuito', False), True)
            else:
                valida_y_crea(imp, 'montoTotalImpuesto' + tipo, dict.get('mont_tot_imp', False), True)
    
            #DNINACO CUANDO ES GRATUITA ESTE TAAG NO DEBE ENVIARSE
            if dict.get('gratuito', False)==False and dict.get('cod_imp', False)!="7152":
                valida_y_crea(imp, 'montoSubTotalImpuesto' + tipo, dict.get('mont_subtot_imp', False), True)
  

#DNINACO SE AGREGO EL PARAMETRO MODELO
def get_trama_guia_remision(dict,metodo,modelo=False):
    
    env_cpe = etree.Element('enviarComprobante')   
    gen_header(env_cpe, dict.get('remit_cod', False), metodo,modelo)
    obj = etree.SubElement(env_cpe, 'comprobanteElectronico')
    valida_y_crea(obj, 'codigoEmisor', dict.get('remit_cod', False), True)
    valida_y_crea(obj, 'codigoTipoDocumentoIdentificacionAdquiriente', dict.get('dest_tipo_doc', False), True)
    valida_y_crea(obj, 'codigoTipoDocumentoIdentificacionEmisor', dict.get('remit_tipo_doc', False), True)
    
    type_conveyor = dict.get('type_conveyor', False)
    if type_conveyor:
        dat_transp = etree.SubElement(obj,'datosTransporte')
        if type_conveyor == 'privado':
            #valida_y_crea(dat_transp, 'numDocIdentiConduct', dict.get('trans_pri_con_num_doc', False), True)
            #valida_y_crea(dat_transp, 'tipDocIdentiConduct', dict.get('trans_pri_con_tipo_doc', False), True)
            #valida_y_crea(dat_transp, 'numPlacaVehicl', dict.get('trans_pri_placa', False), True)
            #MIGUEL:
            valida_y_crea(dat_transp, 'razSocNombreTransprt', dict.get('trans_pub_nombre', False), True)
            valida_y_crea(dat_transp, 'numRucTransprt', dict.get('trans_pri_con_num_doc', False), True)
            valida_y_crea(dat_transp, 'tipDocTransprt', dict.get('trans_pub_tipo_doc', False), True)
            valida_y_crea(dat_transp, 'numDocIdentiConduct', dict.get('trans_pri_con_num_doc', False), True)
            valida_y_crea(dat_transp, 'numPlacaVehicl', dict.get('trans_pri_placa', False), True)
            
            # AGREGAMOS NUEVOS TAGS DATOS DE TRANSPORTE
            valida_y_crea(dat_transp, 'apellidosTransprt', dict.get('apellidosTransprt', False), True)
            valida_y_crea(dat_transp, 'numLicenciaConduct', dict.get('numLicenciaConduct', False), True)
            #
        elif type_conveyor == 'publico':
            valida_y_crea(dat_transp, 'razSocNombreTransprt', dict.get('trans_pub_nombre', False), True)
            valida_y_crea(dat_transp, 'numRucTransprt', dict.get('trans_pub_num_ruc', False), True)
            valida_y_crea(dat_transp, 'tipDocTransprt', dict.get('trans_pub_tipo_doc', False), True)
    
    dat_trasl = etree.SubElement(obj, 'datosTraslado')
    valida_y_crea(dat_trasl, 'codMdldTrasld', dict.get('cod_mod_traslado', False), True)
    valida_y_crea(dat_trasl, 'codMotvTrasld', dict.get('cod_motivo', False), True)
    valida_y_crea(dat_trasl, 'codPuerto', dict.get('cod_puerto', False), True)
    valida_y_crea(dat_trasl, 'descMotvTrasld', dict.get('descripcion', False), True)
    valida_y_crea(dat_trasl, 'fecIniTrasld', dict.get('fecha_ini_traslado', False), True)
    valida_y_crea(dat_trasl, 'indTransbrdProg', dict.get('ind_trans_prog', False), True)
    if dict.get('cod_motivo', False)=='09' or dict.get('description', False)=='EXPORTACION':
        valida_y_crea(dat_trasl, 'codTipDocRelcd', dict.get('cod_num_doc_rel_cd', False), True)      
        valida_y_crea(dat_trasl, 'numDocRelcd', dict.get('num_doc_rel_cd', False), True)
    # El TAG 'numBultos' sólo es necesario cuando se trata de una IMPORTACION, codigo '08'.
    if dict.get('cod_motivo', False)=='08':
        valida_y_crea(dat_trasl, 'numBultos', dict.get('num_bultos', False), True)
    valida_y_crea(dat_trasl, 'numContndr', dict.get('num_contenedor', False), True)
    valida_y_crea(dat_trasl, 'numDocIdentiEstabTer', dict.get('estab_ter_num_doc', False), True)
    valida_y_crea(dat_trasl, 'pesoBrutoTotl', dict.get('peso_bruto_total', False), True)
    valida_y_crea(dat_trasl, 'razSocNombreEstabTer', dict.get('estab_ter_nombre', False), True)
    valida_y_crea(dat_trasl, 'tipDocIdentiEstabTer', dict.get('estab_ter_tipo_doc', False), True)
    valida_y_crea(dat_trasl, 'unidMedPesoBruto', dict.get('unid_med_peso_bruto', False), True)
    
    dir_det = dict.get('dir_lleg_direccion', False)
    ubi = dict.get('dir_lleg_ubigeo', False)
    
    if (dir_det or ubi):
        dir_adq = etree.SubElement(obj, 'direccionAdquiriente')
        valida_y_crea(dir_adq, 'direccionDetallada', dir_det, True)
        valida_y_crea(dir_adq, 'codigoUbigeo', ubi, True)
        valida_y_crea(dir_adq, 'departamento', dict.get('departamento_adq',False), True)
        valida_y_crea(dir_adq, 'distrito', dict.get('distrito_adq',False), True)
        valida_y_crea(dir_adq, 'provincia', dict.get('provincia_adq',False), True)

        # AGREGAMOS NUEVOS TAGS
        valida_y_crea(dir_adq, 'longitud', dict.get('longitud',False), True)
        valida_y_crea(dir_adq, 'latitud', dict.get('latitud',False), True)
        if dict.get('rucAsociado_adq',False) != '':
            valida_y_crea(dir_adq, 'rucAsociado', dict.get('rucAsociado_adq',False), True)
            valida_y_crea(dir_adq, 'codigoSunatAnexo', dict.get('codigoSunatAnexo_adq',False), True)
        #

    dir_det = dict.get('pto_part_direccion', False)
    ubi = dict.get('pto_part_ubigeo', False)
    
    if (dir_det or ubi):
        dir_emi = etree.SubElement(obj, 'direccionEmisor')
        valida_y_crea(dir_emi, 'direccionDetallada', dir_det, True)
        valida_y_crea(dir_emi, 'codigoUbigeo', ubi, True)
        valida_y_crea(dir_emi, 'departamento', dict.get('departamento_emi',False), True)
        valida_y_crea(dir_emi, 'distrito', dict.get('distrito_emi',False), True)
        valida_y_crea(dir_emi, 'provincia', dict.get('provincia_emi',False), True)
	
	# AGREGAMOS NUEVOS TAGS
        valida_y_crea(dir_emi, 'longitud', dict.get('longitud',False), True)
        valida_y_crea(dir_emi, 'latitud', dict.get('latitud',False), True)
        if dict.get('rucAsociado_emi',False)!='':
            valida_y_crea(dir_emi, 'rucAsociado', dict.get('rucAsociado_emi',False), True)
            valida_y_crea(dir_emi, 'codigoSunatAnexo', dict.get('codigoSunatAnexo_emi',False), True)
        #	
    
    number = dict.get('doc_rel_numero', False)
    serie_doc_rel = False
    correlativo_doc_rel = False
    if number and comprobante_pattern.match(number) is not None:
        serie_doc_rel, correlativo_doc_rel = number.split('-')
        
    if dict.get('doc_rel_tipo', False) or correlativo_doc_rel or serie_doc_rel:
        related_doc = etree.SubElement(obj, 'documentosRelacionados')
        valida_y_crea(related_doc, 'codigoTipoDocumento', dict.get('doc_rel_tipo', False), True)
        valida_y_crea(related_doc, 'numeroCorrelativo', correlativo_doc_rel, True)
        valida_y_crea(related_doc, 'serie', serie_doc_rel, True)

        # AGREGAMOS NUEVOS TAGS DOC RELACIONADO
        valida_y_crea(related_doc, 'descripcion', dict.get('descripcion', False), True)
        valida_y_crea(related_doc, 'codTipDocEmisor', dict.get('codTipDocEmisor', False), True)
        valida_y_crea(related_doc, 'rucEmisor', dict.get('rucEmisor', False), True)
        #
    
    valida_y_crea(obj, 'fechaEmision', dict.get('fecha_emision', False), True)

    # AGREGAMOS NUEVOS TAGS DE HORA
    valida_y_crea(obj, 'horaEmision', dict.get('horaEmision', False), True)
    #
    
    gen_cpePagElectKey(obj, dict.get('serie_documento', False), dict.get('numero_documento', False), dict.get('tipo_documento', False), dict.get('remit_num_doc', False))
    
    items = dict.get('items', False)
    if (items):
        for item in items.iterchildren():
            obj.append(item)
    
    
    '''DNINACO AGREGADO EL TAG NECESARIO PARA ENVIAR A EBIS DE UBIGEO Y DIRECCION DE PARTIDA
    del tag de INFORMACION ADICIONAL FACTURA GUIA
    info_adicional = etree.SubElement(obj, 'informacionAdicionalFacturaGuia')
    data = dict.get('dataPartida', False)
    if (data):
        for info in data.iterchildren():
            info_adicional.append(info)
    '''
            
    '''DNINACO AGREGADO EL TAG NECESARIO PARA ENVIAR A EBIS DE UBIGEO Y DIRECCION DE PARTIDA
    del tag direccionPartida'''
    dataDirecPartida = dict.get('dataDirecPartida', False)
    if (dataDirecPartida):
        for direc in dataDirecPartida.iterchildren():
            obj.append(direc)
    
    
    valida_y_crea(obj, 'numeroDocumentoIdentificacionAdquiriente', dict.get('dest_num_doc', False), True)
    
    valida_y_crea(obj, 'observaciones', dict.get('observaciones', False), True)
    valida_y_crea(obj, 'razonSocialAdquiriente', dict.get('dest_nombre', False), True)
    valida_y_crea(obj, 'razonSocialEmisor', dict.get('remit_nombre', False), True)

    # Se agrega el correo electronico
    valida_y_crea(obj, 'correoElectronicoAdquiriente', dict.get('correoElectronicoAdquiriente', False), True)
    
    # Dninaco Agregamos Estructura variable
    tag_estructuras = etree.Element('estructuraVariable')
    if dict.get('tieneEstructura', False):
        for estructura in dict.get('estructuraVariable', False):
            taglistadoDeEstructuras = etree.Element('listadoDeEstructuras')

            valida_y_crea(taglistadoDeEstructuras, 'nombre', estructura.get('nombre', False), True)
            valida_y_crea(taglistadoDeEstructuras, 'valor', estructura.get('valor', False), True)

            tag_estructuras.append(taglistadoDeEstructuras)

    obj.append(tag_estructuras)
    #

    return etree.tostring(env_cpe, pretty_print=True)

# Función para obtener los datos de los productos y/o servicios
def get_datos_items_guia(dict):
    items = etree.Element('itemsComprobantePagoElectronicoVenta')
    valida_y_crea(items, 'cantidad', dict.get('cantidad', False), True)
    valida_y_crea(items, 'codigoProducto', dict.get('item', False), True)
    valida_y_crea(items, 'descripcionProducto', dict.get('descripcion', False), True)
    valida_y_crea(items, 'numeroOrden', dict.get('num_orden', False), True)
    valida_y_crea(items, 'unidadMedida', dict.get('unidad_medida', False), True)
    valida_y_crea(items, 'pesoTotalItem', dict.get('peso_total_item', False), True)

    # ESTRURCUTRA VARIABLE
    # Dninaco Agregamos Estructura variable
    tag_estructuras = etree.Element('estructuraVariable')
    if dict.get('tieneEstructura', False):
        for estructura in dict.get('estructuraVariable', False):
            taglistadoDeEstructuras = etree.Element('listadoDeEstructuras')

            valida_y_crea(taglistadoDeEstructuras, 'nombre', estructura.get('nombre', False), True)
            valida_y_crea(taglistadoDeEstructuras, 'valor', estructura.get('valor', False), True)

            tag_estructuras.append(taglistadoDeEstructuras)

    items.append(tag_estructuras)
    #

    dict['lst_items'] = items

# Función para llenar el tag direccionPartida
'''@author DNINACO'''
def get_direccion_partida(dict):
    direccion_partida = etree.Element('direccionPartida')
    valida_y_crea(direccion_partida, 'codigoUbigeo', dict.get('codigoUbigeo', False), True)
    valida_y_crea(direccion_partida, 'direccionDetallada', dict.get('direccionDetallada', False), True)
    if dict.get('codigoSunatAnexo',False) != '':
        valida_y_crea(direccion_partida, 'codigoSunatAnexo', dict.get('codigoSunatAnexo',False), True)
        valida_y_crea(direccion_partida, 'rucAsociado', dict.get('rucAsociado',False), True)
    dict['direc_partida'] = direccion_partida
