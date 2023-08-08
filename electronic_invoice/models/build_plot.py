# -*- coding: utf-8 -*-

from odoo import models, fields, api

import base64
import datetime
import logging
import hashlib
import time
import re

from datetime import datetime
from lxml import etree
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

# import HTTPSHandler
# from urllib3 import HTTPSHandler
# import ssl

from requests import Session
from zeep import Client as ClientZepp
from zeep.transports import Transport

from odoo import _, tools
# from except_error import WebServiceError
from xml.sax.saxutils import escape
from docutils.nodes import author
from _ast import Not

TIPOS_COMPROBANTE = {
        'FACTURA':'01',
        'BOLETA':'03',
        'NOTA_CREDITO':'07',
        'NOTA_DEBITO':'08',
        'GUIA_REMISION_REMITENTE':'09',
        'NOTA_PEDIDO':'NP',
    }

_logger = logging.getLogger(__name__)

comprobante_pattern = re.compile(r'^\w{4}-\d{1,8}$')


class account_move(models.Model):
    _inherit = 'account.move'
    
    def get_respuesta_zeep(self, url, metodo, trama):
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
        except:
            print('Error de Web Service')

    def get_token(self, cod_emisor, fecha_transac, metodo, psw):
        token = False
        if (cod_emisor and fecha_transac and metodo and psw) :
            cadena = cod_emisor + fecha_transac + metodo + psw
            m = hashlib.sha1()
            m.update(cadena.encode())
            token = base64.b64encode(m.digest())
        return token

    def valida_y_crea(self, obj, tag, txt, Sub):
    
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

    def gen_header(self, obj, dict, metodo):
        #SE MODIFICO PARA QUE TRAIGA LO QUE SE CONFIGURO EN LA COMPANIA
        psw = dict['pass_security']
        codigoEmisor = dict['codigoEmisor']
        
        metodo = metodo + 'Request'
        
        fecha_transac = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        
        token = self.get_token(codigoEmisor, fecha_transac, metodo, psw)
        
        header = etree.Element("header")
        
        self.valida_y_crea(header, 'fechaTransaccion', fecha_transac, True)
        self.valida_y_crea(header, 'idEmisor', codigoEmisor, True)
        self.valida_y_crea(header, 'token', token, True)
        self.valida_y_crea(header, 'transaccion', metodo, True)
        
        obj.append(header)

    #DNINACO SE AGREGO EL ATRIBUTO MODELO
    def get_trama_Cpe_Pago(self, dict, metodo):
        
        cpe_pago_pet = etree.Element('enviarComprobante')
        
        # Se agrega el tag de cabezera
        self.gen_header(cpe_pago_pet, dict, metodo)
        
        # Creamos el tag de comprobate electronico
        tag_comp_elect = etree.SubElement(cpe_pago_pet, 'comprobanteElectronico')
        
        self.valida_y_crea(tag_comp_elect, 'anticipo', dict.get('anticipo', False), True)
        # armamos el tag de deduccion de anticipos
        if dict.get('deduccion', False):
            for anticipos in dict.get('lista_anticipos', False):
                tag_anticipos = etree.Element('anticipos')
                self.valida_y_crea(tag_anticipos, 'codigoTipoDocumento', anticipos.get('codigoTipoDocumento', False), True)
                self.valida_y_crea(tag_anticipos, 'descripcion', anticipos.get('descripcion', False), True)
                self.valida_y_crea(tag_anticipos, 'montoImporteValorVenta', anticipos.get('montoImporteValorVenta', False), True)
                self.valida_y_crea(tag_anticipos, 'montoTotal', anticipos.get('montoTotal', False), True)
                self.valida_y_crea(tag_anticipos, 'numeroCorrelativo', anticipos.get('numeroCorrelativo', False), True)
                self.valida_y_crea(tag_anticipos, 'serie', anticipos.get('serie', False), True)
                tag_comp_elect.append(tag_anticipos)

        #
        self.valida_y_crea(tag_comp_elect, 'codTipoOperacion', dict.get('codTipoOperacion', False), True)
        self.valida_y_crea(tag_comp_elect, 'codigoEmisor', dict.get('codigoEmisor', False), True)
        self.valida_y_crea(tag_comp_elect, 'codigoTipoDocumentoIdentificacionAdquiriente', dict.get('codigoTipoDocumentoIdentificacionAdquiriente', False), True)
        self.valida_y_crea(tag_comp_elect, 'codigoTipoDocumentoIdentificacionEmisor', dict.get('codigoTipoDocumentoIdentificacionEmisor', False), True)
        self.valida_y_crea(tag_comp_elect, 'codigoTipoMoneda', dict.get('codigoTipoMoneda', False), True)
        
        #DNINACO SE REALIZA EL DESARROLLO PARA EL ENVIO DE DESCUENTO GLOBAL
        if  dict.get('tiene_desc_global', False):
            descuento_cargo_global = etree.Element('descuentoCargoGlobal')
            self.valida_y_crea(descuento_cargo_global, 'descuentoNoAfectaIGV', dict.get('sum_total_desc', False), True)
            self.valida_y_crea(descuento_cargo_global, 'indicador','false', True)
            tag_comp_elect.append(descuento_cargo_global)

        self.valida_y_crea(tag_comp_elect, 'descuentoGlobal', dict.get('sum_total_desc', False), True)
        self.valida_y_crea(tag_comp_elect, 'totalDscNoAfecta', dict.get('sum_total_desc', False), True)
        
        # Creamos el tag direccion adquiriente
        tag_dir_adqui = etree.Element('direccionAdquiriente')
        dir_adquiriente = dict['direccionAdquiriente']
        self.valida_y_crea(tag_dir_adqui, 'codigoPais', dir_adquiriente.get('codigoPais', False), True)
        self.valida_y_crea(tag_dir_adqui, 'departamento', dir_adquiriente.get('departamento', False), True)
        self.valida_y_crea(tag_dir_adqui, 'direccionDetallada', dir_adquiriente.get('direccionDetallada', False), True)
        self.valida_y_crea(tag_dir_adqui, 'distrito', dir_adquiriente.get('distrito', False), True)
        self.valida_y_crea(tag_dir_adqui, 'provincia', dir_adquiriente.get('provincia', False), True)

        tag_comp_elect.append(tag_dir_adqui)

        # Creamos el tag direccion emisor
        tag_dir_emisor = etree.Element('direccionEmisor')
        dir_emisor = dict['direccionEmisor']
        self.valida_y_crea(tag_dir_emisor, 'codigoSunatAnexo', dir_emisor.get('codigoSunatAnexo', False), True)
        self.valida_y_crea(tag_dir_emisor, 'codigoPais', dir_emisor.get('codigoPais', False), True)
        self.valida_y_crea(tag_dir_emisor, 'departamento', dir_emisor.get('departamento', False), True)
        self.valida_y_crea(tag_dir_emisor, 'direccionDetallada', dir_emisor.get('direccionDetallada', False), True)
        self.valida_y_crea(tag_dir_emisor, 'distrito', dir_emisor.get('distrito', False), True)
        self.valida_y_crea(tag_dir_emisor, 'provincia', dir_emisor.get('provincia', False), True)

        tag_comp_elect.append(tag_dir_emisor)

        # no hay estrutura variable

        self.valida_y_crea(tag_comp_elect, 'fechaEmision', dict.get('fechaEmision', False), True)
        self.valida_y_crea(tag_comp_elect, 'fechaVencimiento', dict.get('fechaVencimiento', False), True)
        self.valida_y_crea(tag_comp_elect, 'horaEmision', dict.get('horaEmision', False), True)

        # Creamos el tag identificador
        tag_identificador = etree.Element('identificador')
        identificador = dict['identificador']
        self.valida_y_crea(tag_identificador, 'codigoTipoDocumento', identificador.get('codigoTipoDocumento', False), True)
        self.valida_y_crea(tag_identificador, 'numeroCorrelativo', identificador.get('numeroCorrelativo', False), True)
        self.valida_y_crea(tag_identificador, 'numeroDocumentoIdentificacionEmisor', identificador.get('numeroDocumentoIdentificacionEmisor', False), True)
        self.valida_y_crea(tag_identificador, 'serie', identificador.get('serie', False), True)
        self.valida_y_crea(tag_identificador, 'letraIniTipoDocFisico', identificador.get('letraIniTipoDocFisico', False), True)
        self.valida_y_crea(tag_identificador, 'tipoEmision', identificador.get('tipoEmision', False), True)

        tag_comp_elect.append(tag_identificador)

        self.valida_y_crea(tag_comp_elect, 'importeTotal', dict.get('importeTotal', False), True)
        self.valida_y_crea(tag_comp_elect, 'indicadorOperacionSujetaDetraccion', dict.get('indicadorOperacionSujetaDetraccion', False), True)

        # Creamos los tags de items
        for item in dict.get('lista_items', False):
            tag_element = etree.Element('itemsComprobantePagoElectronicoVenta')
            self.valida_y_crea(tag_element, 'cantidad', item.get('cantidad', False), True)
            self.valida_y_crea(tag_element, 'descripcionProducto', item.get('descripcionProducto', False), True)
            self.valida_y_crea(tag_element, 'detalleProducto', item.get('detalleProducto', False), True)
            if dict.get('gratuito', False):
                self.valida_y_crea(tag_element, 'importeValorVentaItem', item.get('importeValorVentaItem', False), True)
            else:
                self.valida_y_crea(tag_element, 'importeValorVentaItem', item.get('importeValorVentaItem', False), True)
            self.valida_y_crea(tag_element, 'importeTotal', item.get('importeTotal', False), True)

            # creamos el tag impuestos unitarios se modifica para agregar una lista
            imp_unit_dicts = item.get('impuestosUnitarios', False)
            for imp_unit_dict in imp_unit_dicts:
                tag_imp_unit = etree.Element('impuestosUnitarios')
                if imp_unit_dict.get('codigoImpuestoUnitario', False) != '7152':
                    self.valida_y_crea(tag_imp_unit, 'codigoImpuestoUnitario', imp_unit_dict.get('codigoImpuestoUnitario', False), True)
                    self.valida_y_crea(tag_imp_unit, 'codigoInternacionalImpuesto', imp_unit_dict.get('codigoInternacionalImpuesto', False), True)
                    self.valida_y_crea(tag_imp_unit, 'codigoTipoAfectacionIgv', imp_unit_dict.get('codigoTipoAfectacionIgv', False), True)
                    self.valida_y_crea(tag_imp_unit, 'montoBaseImpuesto', imp_unit_dict.get('montoBaseImpuesto', False), True)
                    if not dict.get('gratuito', False):
                        self.valida_y_crea(tag_imp_unit, 'tasaImpuesto', imp_unit_dict.get('tasaImpuesto', False), True)
                        self.valida_y_crea(tag_imp_unit, 'nombreImpuestoUnitario', imp_unit_dict.get('nombreImpuestoUnitario', False), True)
                    self.valida_y_crea(tag_imp_unit, 'montoTotalImpuestoUnitario', imp_unit_dict.get('montoTotalImpuestoUnitario', False), True)
                    self.valida_y_crea(tag_imp_unit, 'montoSubTotalImpuestoUnitario', imp_unit_dict.get('montoSubTotalImpuestoUnitario', False), True)
                else:
                    self.valida_y_crea(tag_imp_unit, 'codigoImpuestoUnitario', imp_unit_dict.get('codigoImpuestoUnitario', False), True)
                    self.valida_y_crea(tag_imp_unit, 'montoTotalImpuestoUnitario', imp_unit_dict.get('montoTotalImpuestoUnitario', False), True)
                    self.valida_y_crea(tag_imp_unit, 'montoUnitario', imp_unit_dict.get('montoUnitario', False), True)  

                tag_element.append(tag_imp_unit)

            self.valida_y_crea(tag_element, 'indicadorDescuento', item.get('indicadorDescuento', False), True)
            self.valida_y_crea(tag_element, 'montoDescuento', item.get('montoDescuento', False), True)
            self.valida_y_crea(tag_element, 'numeroOrden', item.get('numeroOrden', False), True)

            # creamos el tag precios unitarios
            tag_prec_unit = etree.Element('preciosUnitarios')
            prec_unit = item.get('preciosUnitarios', False)
            self.valida_y_crea(tag_prec_unit, 'codigoTipoPrecio', prec_unit.get('codigoTipoPrecio', False), True)
            self.valida_y_crea(tag_prec_unit, 'montoPrecio', prec_unit.get('montoPrecio', False), True)

            tag_element.append(tag_prec_unit)

            self.valida_y_crea(tag_element, 'unidadMedida', item.get('unidadMedida', False), True)
            self.valida_y_crea(tag_element, 'valorVentaUnitario', item.get('valorVentaUnitario', False), True)

            # Se agrega el codigo de sunat al envio si es qeu existe
            self.valida_y_crea(tag_element, 'codigoSUNAT', item.get('codigoSUNAT', False), True)
            #

            tag_comp_elect.append(tag_element)

        # Agregamos el tag para NC y ND
        if dict.get('rectificativa', False):
            self.valida_y_crea(tag_comp_elect, 'codigoTipoNota', dict.get('codigoTipoNota', False), True)
            
            tag_doc_modify = etree.Element('documentosModificados')
            doc_modify = dict.get('documentosModificados', False)
            self.valida_y_crea(tag_doc_modify, 'codigoTipoDocumento', doc_modify.get('codigoTipoDocumento', False), True)
            self.valida_y_crea(tag_doc_modify, 'fechaEmision', doc_modify.get('fechaEmision', False), True)
            self.valida_y_crea(tag_doc_modify, 'serie', doc_modify.get('serie', False), True)
            self.valida_y_crea(tag_doc_modify, 'numeroCorrelativo', doc_modify.get('numeroCorrelativo', False), True)
            
            tag_comp_elect.append(tag_doc_modify)
            self.valida_y_crea(tag_comp_elect, 'motivoNota', dict.get('motivoNota', False), True)

        # evaluamos para agregar el tag de detraccion
        if dict.get('indicadorOperacionSujetaDetraccion',False)=='S':
            elem_adicional = etree.SubElement(tag_comp_elect, 'propiedadesAdicionales')
            self.valida_y_crea(elem_adicional, 'codigoPropiedadAdicional', '2006', True)
            self.valida_y_crea(elem_adicional, 'descripcionPropiedadAdicional', u'Leyenda: Operación sujeta a detracción', True)

            tag_detra = etree.SubElement(tag_comp_elect,'detalleDetraccion')
            detalle_detra = dict.get('detalleDetraccion', False)
            self.valida_y_crea(tag_detra,'codigoBienOSevicio' ,detalle_detra.get('codigoBienOSevicio', False), True)
            self.valida_y_crea(tag_detra,'medioPago' , detalle_detra.get('medioPago', False), True)
            self.valida_y_crea(tag_detra,'monto' ,detalle_detra.get('monto', False), True)
            self.valida_y_crea(tag_detra,'montoBase' , detalle_detra.get('montoBase', False), True)
            self.valida_y_crea(tag_detra,'porcentaje' , detalle_detra.get('porcentaje', False), True)
        
        self.valida_y_crea(tag_comp_elect, 'razonSocialAdquiriente', dict.get('razonSocialAdquiriente', False), True)
        self.valida_y_crea(tag_comp_elect, 'nombresAdquiriente', dict.get('nombresAdquiriente', False), True)
        self.valida_y_crea(tag_comp_elect, 'nombreComercialEmisor', dict.get('nombreComercialEmisor', False), True)
        self.valida_y_crea(tag_comp_elect, 'numeroDocumentoIdentificacionAdquiriente', dict.get('numeroDocumentoIdentificacionAdquiriente', False), True)
        self.valida_y_crea(tag_comp_elect, 'razonSocialEmisor', dict.get('razonSocialEmisor', False), True)
        self.valida_y_crea(tag_comp_elect, 'telefonoEmisor', dict.get('telefonoEmisor', False), True)
        
        # Dninaco Agregamos los datos de la orden de compra y documentos relacionados
        if dict.get('tieneOrden', False):
            self.valida_y_crea(tag_comp_elect, 'ordenCompra', dict.get('ordenCompra', False), True)
        
        if dict.get('tieneDocumento', False):
            for documento in dict.get('documentos_relacionados', False):
                tag_documento_relacionado = etree.Element('documentosRelacionados')

                self.valida_y_crea(tag_documento_relacionado, 'codigoTipoDocumento', documento.get('codigoTipoDocumento', False), True)
                self.valida_y_crea(tag_documento_relacionado, 'numeroCorrelativo', documento.get('numeroCorrelativo', False), True)
                self.valida_y_crea(tag_documento_relacionado, 'serie', documento.get('serie', False), True)

                tag_comp_elect.append(tag_documento_relacionado)
        #

        # Dninaco Agregamos Estructura variable
        tag_estructuras = etree.Element('estructuraVariable')
        if dict.get('tieneEstructura', False):
            for estructura in dict.get('estructuraVariable', False):
                taglistadoDeEstructuras = etree.Element('listadoDeEstructuras')

                self.valida_y_crea(taglistadoDeEstructuras, 'nombre', estructura.get('nombre', False), True)
                self.valida_y_crea(taglistadoDeEstructuras, 'valor', estructura.get('valor', False), True)

                tag_estructuras.append(taglistadoDeEstructuras)

        tag_comp_elect.append(tag_estructuras)
        #
        
        # Dninaco Observaciones
        self.valida_y_crea(tag_comp_elect, 'observaciones', dict.get('observaciones', False), True)
        #

        self.valida_y_crea(tag_comp_elect, 'totalAnticipo', dict.get('totalAnticipo', False), True)
        self.valida_y_crea(tag_comp_elect, 'totalIgv', dict.get('totalIgv', False), True)
        self.valida_y_crea(tag_comp_elect, 'totalIcbper', dict.get('totalIcbper', False), True)
        self.valida_y_crea(tag_comp_elect, 'totalIsc', dict.get('totalIsc', False), True)
        self.valida_y_crea(tag_comp_elect, 'totalImpuesto', dict.get('totalImpuesto', False), True)
        self.valida_y_crea(tag_comp_elect, 'totalPrecioVenta', dict.get('totalPrecioVenta', False), True)
        self.valida_y_crea(tag_comp_elect, 'totalValorVenta', dict.get('totalValorVenta', False), True)
        self.valida_y_crea(tag_comp_elect, 'totalValorVentaOperacionesGravadas', dict.get('totalValorVentaOperacionesGravadas', False), True)
        self.valida_y_crea(tag_comp_elect, 'totalValorVentaOperacionesExoneradas', dict.get('totalValorVentaOperacionesExoneradas', False), True)
        self.valida_y_crea(tag_comp_elect, 'totalValorVentaOperacionesInafectas', dict.get('totalValorVentaOperacionesInafectas', False), True)
        # Operaciones gratuitas
        operacionesGratuitas = dict.get('operacionesGratuitas', False)
        self.valida_y_crea(tag_comp_elect, 'totalOperacionGratuito', operacionesGratuitas.get('totalOperacionGratuito', False), True)
        self.valida_y_crea(tag_comp_elect, 'totalTributoGratuito', operacionesGratuitas.get('totalTributoGratuito', False), True)
        #
        self.valida_y_crea(tag_comp_elect, 'totalOperacionExportacion', dict.get('totalOperacionExportacion', False), True)
        self.valida_y_crea(tag_comp_elect, 'correoElectronicoAdquiriente', dict.get('correoElectronicoAdquiriente', False), True)
        self.valida_y_crea(tag_comp_elect, 'ventaItinerante', dict.get('ventaItinerante', False), True)

        # FORMAS DE PAGO
        self.valida_y_crea(tag_comp_elect, 'formaPago', dict.get('formaPago', False), True)

        tagformaPagoSUNAT = etree.Element('formaPagoSUNAT')
        self.valida_y_crea(tagformaPagoSUNAT, 'formaPago', dict.get('formaPago2', False), True)

        if  dict.get('formaPago', False) == 'CRE':
            for cuota in dict.get('listadoDeCuotas', False):
                    taglistadoDeCuotas = etree.Element('listadoDeCuotas')

                    self.valida_y_crea(taglistadoDeCuotas, 'fechaVenPago', cuota.get('fechaVenPago', False), True)
                    self.valida_y_crea(taglistadoDeCuotas, 'montoPago', cuota.get('montoPago', False), True)
                    self.valida_y_crea(taglistadoDeCuotas, 'nombre', cuota.get('nombre', False), True)

                    tagformaPagoSUNAT.append(taglistadoDeCuotas)

            self.valida_y_crea(tagformaPagoSUNAT, 'montoNetoPenPago', dict.get('montoNetoPenPago', False), True)
        
        tag_comp_elect.append(tagformaPagoSUNAT)

        #

        return etree.tostring(cpe_pago_pet, pretty_print=True)
    
    def contruir_trama_consulta_respuesta(self, cod_emisor=False, metodo=False, lista=False, guias=False):
		
        obj_company = self.env['res.company'].search([('emisor_code', '=', cod_emisor)])

        pass_security = obj_company.pass_security
		
        list_docs = etree.Element('listaComprobantes')
        dict_list = {'numerodocumento' : obj_company.partner_id.vat}
        if lista and len(lista) > 0:
            for cpe_pend in lista :
                # obj_journal = self.pool.get('account.journal').browse_to(cr, uid, cpe_pend.journal_id, context=context)
                dict_list['tipo_documento'] = cpe_pend.journal_id.sunat_document_type.code
                # if cpe_pend.journal_id.api_code:
                #     serie, correlativo = cpe_pend.name.split('-')
                #     correlativo=int(correlativo)
                #     dict_list['number'] = serie+"-"+str(correlativo)
                # else:
                dict_list['number'] = cpe_pend.name
                dict_list['list_docs'] = ''
                self.get_trama_list_cpe(dict_list)
                if len(dict_list['list_docs']) > 0:
                    list_docs.append(dict_list['list_docs'])

        if guias and len(guias) > 0:
            for cpe_pend in guias :
                # obj_journal = self.pool.get('account.journal').browse_to(cr, uid, cpe_pend.journal_id, context=context)
                dict_list['tipo_documento'] = TIPOS_COMPROBANTE['GUIA_REMISION_REMITENTE']
                dict_list['number'] = cpe_pend.number_sunat
                dict_list['list_docs'] = ''
                self.get_trama_list_cpe(dict_list)
                if len(dict_list['list_docs']) > 0:
                    list_docs.append(dict_list['list_docs'])

        dict = {'codigoEmisor' : cod_emisor,
                'pass_security' : pass_security,
                'list_docs' : list_docs, }

        #dninaco se agrego el obj_company_rel
        trama = self.get_trama_est_cpe(metodo, dict)
		
        return trama
    
    def get_trama_list_cpe(self, dict):
        cpe = etree.Element('comprobante')

        tipo_doc = dict.get('tipo_documento', False)

        # para obtener la serie y correlativo
        number = dict.get('number', False)
        serie = False
        correlativo = False

        if number and number is not None:
            serie, correlativo = number.split('-')
                
            num_doc_id_emi = dict.get('numerodocumento', False)
            
            self.valida_y_crea(cpe, 'tipoDocumento', tipo_doc, True)
            self.valida_y_crea(cpe, 'serie', serie, True)
            self.valida_y_crea(cpe, 'correlativo', correlativo, True)
            self.valida_y_crea(cpe, 'rucEmisor', num_doc_id_emi, True)
            
            dict['list_docs'] = cpe
        else:
            print('Error al momento de agregar valores')

    def get_trama_est_cpe(self, metodo, dict):
        cons_est_cpe = etree.Element('consultarEstadoComprobante')
        cod_emi = dict['codigoEmisor']
        self.gen_header(cons_est_cpe, dict, metodo)
        self.valida_y_crea(cons_est_cpe, 'idEmisor', cod_emi, True)
        
        list = dict.get('list_docs', False)
        
        if len(list) :
            cons_est_cpe.append(list)
        
        return etree.tostring(cons_est_cpe, pretty_print=True)
    
    def get_trama_print_invoice(self, dict, metodo):
        cod_emi = dict.get('codigoEmisor', False)
        imp_cpe_pago_pet = etree.Element('wsImprimirComprobantePagoPeticion')
        self.valida_y_crea(imp_cpe_pago_pet, 'codigoEmisor', cod_emi, True)
        
        # para obtener la serie y correlativo
        number = dict.get('number', False)
        serie = False
        correlativo = False
        if number and comprobante_pattern.match(number) is not None:
            serie, correlativo = number.split('-')
        
        self.gen_header(imp_cpe_pago_pet, dict, metodo)
        
        tipo_doc = dict.get('codigoTipoDocumento', False) #get_tipo_doc(dict.get('journal_code', False))
        num_doc_id_emi = dict.get('numeroDocumentoIdentificacionEmisor', False)
        
        self.gen_cpePagElectKey(imp_cpe_pago_pet, serie, correlativo, tipo_doc, num_doc_id_emi)
        self.valida_y_crea(imp_cpe_pago_pet, 'fechaEmision', dict.get('fechaEmision', False), True)
        tipo_desc = dict.get('tipo_desc', False)
            
        if tipo_desc and tipo_desc == u'TXT':
            self.valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionTxt', 'S', True)
            self.valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionXml', 'N', True)
            self.valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionPdf', 'N', True)
        elif tipo_desc and tipo_desc == u'XML':
            self.valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionTxt', 'N', True)
            self.valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionXml', 'S', True)
            self.valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionPdf', 'N', True)
        else:
            self.valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionTxt', 'N', True)
            self.valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionXml', 'S', True)
            self.valida_y_crea(imp_cpe_pago_pet, 'indicadorPeticionPdf', 'S', True)
        
        self.valida_y_crea(imp_cpe_pago_pet, 'indicadorTipoDocumento', 'V', True)
        return etree.tostring(imp_cpe_pago_pet, pretty_print=True)
    
    def get_trama_baja_cpe_pago(self, dict, metodo):
        baja_pet = etree.Element('enviarSolicitudBaja')

        self.gen_header(baja_pet, dict, metodo)

        baja = etree.SubElement(baja_pet, 'solicitudBaja')
        self.valida_y_crea(baja, 'codigoEmisor', dict.get('codigoEmisor', False), True)
        self.valida_y_crea(baja, 'codigoTipoDocumentoIdentificacionEmisor', dict.get('cod_tipo_doc_emi', False), True)

        # para obtener la serie y correlativo
        number = dict.get('number', False)
        serie = False
        correlativo = False
        if number and comprobante_pattern.match(number) is not None:
            serie, correlativo = number.split('-')

        tipo_doc = dict.get('tipo_documento', False) #get_tipo_doc(dict.get('journal_code', False))

        if ('F' or 'B') in serie:
         if not self.journal_id.is_contg:
            self.gen_cpePagElectKey(baja, serie, correlativo, tipo_doc, dict.get('num_doc_id_emi', False))
        else:
         self.gen_cpePagElectKey(baja, serie, correlativo, tipo_doc, dict.get('num_doc_id_emi', False),dict)

        self.valida_y_crea(baja, 'fechaEmisionBajaCpe', dict.get('fec_emi', False), True)
        self.valida_y_crea(baja, 'horaEmisionBajaCpe', dict.get('hora_emi', False), True)
        self.valida_y_crea(baja, 'motivoBaja', dict.get('motivo', False), True)
        self.valida_y_crea(baja, 'razonSocialEmisor', dict.get('raz_soc_emi', False), True)

        return etree.tostring(baja_pet, pretty_print=True)

    def gen_cpePagElectKey(self, obj, serie, correlativo, tipoDoc, numDocIdEmi,dict=None):
        cpePagoElectVentaKey = etree.Element("identificador")

        self.valida_y_crea(cpePagoElectVentaKey, 'codigoTipoDocumento', tipoDoc, True)
        self.valida_y_crea(cpePagoElectVentaKey, 'numeroCorrelativo', correlativo, True)
        self.valida_y_crea(cpePagoElectVentaKey, 'numeroDocumentoIdentificacionEmisor', numDocIdEmi, True)
        self.valida_y_crea(cpePagoElectVentaKey, 'serie', serie, True)

        if dict:     
            if tipoDoc=='01':
                self.valida_y_crea(cpePagoElectVentaKey, 'letraIniTipoDocFisico', 'F', True) 
            if tipoDoc=='03':
                self.valida_y_crea(cpePagoElectVentaKey, 'letraIniTipoDocFisico', 'B', True)
            
            if tipoDoc=='07' or tipoDoc=='08': 
                if self.related_document_type =='01':
                    self.valida_y_crea(cpePagoElectVentaKey, 'letraIniTipoDocFisico', 'F', True) 
                if self.related_document_type == '03':
                    self.valida_y_crea(cpePagoElectVentaKey, 'letraIniTipoDocFisico', 'B', True)
            
            self.valida_y_crea(cpePagoElectVentaKey, 'tipoEmision', 'FIS', True)
                
        obj.append(cpePagoElectVentaKey)
