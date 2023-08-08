# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import time

import datetime

from datetime import datetime, date, time
from odoo.exceptions import UserError, UserError


class account_move(models.Model):
    _inherit = 'account.move'

    def build_dict_send_invoice(self):

        data_invoice = {}

        invoice = self

        company_obj = self.company_id
        company_partner_id = company_obj.partner_id
        type_identification_company = company_partner_id.l10n_latam_identification_type_id

        client_obj = self.partner_id
        type_identification_client = client_obj.l10n_latam_identification_type_id

        journal_obj = self.journal_id

        # Realizamos las validaciones para la emision
        self.invoice_validate()
        self.export_invoice_validate()
        self.cuotas_validate()

        data_invoice['pass_security'] = company_obj.pass_security
        data_invoice['anticipo'] = False if not invoice.anticipo else True
        data_invoice['codTipoOperacion'] = invoice.operation_type.code
        data_invoice['codigoEmisor'] = company_obj.emisor_code
        data_invoice['codigoTipoDocumentoIdentificacionAdquiriente'] = type_identification_client.l10n_pe_vat_code
        data_invoice['codigoTipoDocumentoIdentificacionEmisor'] = type_identification_company.l10n_pe_vat_code
        data_invoice['codigoTipoMoneda'] = invoice.currency_id.name
        
        direccionAdquiriente = {}
        direccionAdquiriente['codigoPais'] = client_obj.country_id.code
        direccionAdquiriente['departamento'] = client_obj.state_id.name
        direccionAdquiriente['provincia'] = client_obj.city_id.name
        direccionAdquiriente['distrito'] = client_obj.l10n_pe_district.name
        direccionAdquiriente['direccionDetallada'] = client_obj.street
        data_invoice['direccionAdquiriente'] = direccionAdquiriente

        direccionEmisor = {}
        # dninaco Falta ver la manera de obtener este campo
        sale_order = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)])

        #if sale_order:
        #    direccionEmisor['codigoSunatAnexo'] = sale_order.warehouse_id.warehouse_annex_code
        #else:
        almacen = invoice.journal_id.almacen
        direccionEmisor['codigoSunatAnexo'] = '0000' if not almacen.warehouse_annex_code else almacen.warehouse_annex_code

        direccionEmisor['codigoPais'] = almacen.partner_id.country_id.code #company_partner_id.country_id.code
        direccionEmisor['departamento'] = almacen.partner_id.state_id.name #company_partner_id.state_id.name
        direccionEmisor['provincia'] = almacen.partner_id.city_id.name #company_partner_id.city_id.name
        direccionEmisor['distrito'] = almacen.partner_id.l10n_pe_district.name #company_partner_id.l10n_pe_district.name
        direccionEmisor['direccionDetallada'] = almacen.partner_id.street #company_partner_id.street
        data_invoice['direccionEmisor'] = direccionEmisor

        # dninaco Falta agregar estructura variable
        data_invoice['fechaEmision'] = invoice.invoice_date.strftime(
            '%Y-%m-%d')
        data_invoice['fechaVencimiento'] = invoice.invoice_date_due.strftime(
            '%Y-%m-%d')

        data_invoice['horaEmision'] = invoice.write_date.strftime('%H:%M:%S')

        identificador = {}
        serie, correlativo = invoice.name.split('-')
        
        if invoice.move_type == 'out_refund':
            identificador['codigoTipoDocumento'] = journal_obj.sunat_document_type_related.code
        else:
            identificador['codigoTipoDocumento'] = journal_obj.sunat_document_type.code
        
        identificador['numeroDocumentoIdentificacionEmisor'] = company_partner_id.vat
        identificador['serie'] = serie
        identificador['numeroCorrelativo'] = correlativo
        
        #para la contingencia
        if ('F' or 'B') not in serie:
         if invoice.journal_id.is_contg:
            identificador['tipoEmision'] = 'FIS'

            if identificador['codigoTipoDocumento']=='01':
                identificador['letraIniTipoDocFisico'] = 'F'
            if identificador['codigoTipoDocumento']=='03':
                identificador['letraIniTipoDocFisico'] = 'B'
            
            if identificador['codigoTipoDocumento']=='07' or identificador['codigoTipoDocumento']=='08':
                if invoice.related_document_type =='01':
                    identificador['letraIniTipoDocFisico'] = 'F'
                if invoice.related_document_type == '03':
                    identificador['letraIniTipoDocFisico'] = 'B'
        #

        data_invoice['identificador'] = identificador

        data_invoice['importeTotal'] = invoice.amount_total

        if invoice.active_detraction:
            data_invoice['indicadorOperacionSujetaDetraccion'] = 'S'
            detalleDetraccion = {}
            detalleDetraccion['codigoBienOSevicio'] = invoice.service_detraction.code
            detalleDetraccion['medioPago'] = invoice.type_paid_detraction.code
            detalleDetraccion['monto'] = invoice.amount_detraction
            detalleDetraccion['montoBase'] = invoice.amount_total
            detalleDetraccion['porcentaje'] = invoice.rate_detraction

            data_invoice['detalleDetraccion'] = detalleDetraccion

        else:
            data_invoice['indicadorOperacionSujetaDetraccion'] = 'N'

        # items de la venta
        lista_items = []

        orden = 0

        # inicializamos variables de acumulacion
        sum_gravada = 0.00
        sum_exonerada = 0.00
        sum_inafecta = 0.00
        sum_exportacion = 0.00
        sum_gratuitas = 0.00
        sum_imp_bolsa = 0.00

        desct_global = False
        amount_desct_global = 0.00
        
        total_gratuitos = 0.00
        total_tributos_gratuitos = 0.00
        data_invoice['gratuito'] = False

        list_anticipos = []
        data_invoice['deduccion'] = False
        totalAnticipo = 0.00
        subtotal_anticipos = 0.00
        impuesto_anticipos = 0.00

        # para ordenar por id
        # lineas_factura = self.env['account.move.line'].search([('move_id', '=', invoice.id), ('exclude_from_invoice_tab', '=', False)], order='id asc')

        # for invoice_line in invoice.invoice_line_ids:
        for invoice_line in invoice.invoice_line_ids:
            # Identificamos si es una seccion
            if invoice_line.display_type not in ('line_section', 'line_note'):
                item = {}
                gratuito = False
                # Agregamos el codigo de sunat a la trama
                item['codigoSUNAT'] = ''
                if invoice_line.product_id:
                    item['codigoSUNAT'] = invoice_line.product_id.product_tmpl_id.sunat_code
                #

                if invoice_line.price_subtotal >=0:
                    item['cantidad'] = invoice_line.quantity
                    item['descripcionProducto'] = invoice_line.name if len(invoice_line.name) <= 500 else invoice_line.product_id.name
                    item['detalleProducto'] = invoice_line.name if len(invoice_line.name) > 500 else ''
                    item['importeValorVentaItem'] = invoice_line.price_subtotal
                    item['importeTotal'] = invoice_line.price_total

                    # se realiza el cambio para lista de impuestos
                    lista_impuesto = []
                    tax_id_objs = invoice_line.tax_ids
                    for  tax_id_obj in tax_id_objs:
                        impuestosUnitarios = {}
                        if tax_id_obj.l10n_pe_edi_tax_code != '7152':
                            impuestosUnitarios['codigoImpuestoUnitario'] = tax_id_obj.l10n_pe_edi_tax_code
                            impuestosUnitarios['codigoInternacionalImpuesto'] = tax_id_obj.tax_internactional_code
                            impuestosUnitarios['codigoTipoAfectacionIgv'] = tax_id_obj.igv_affectation.code
                            
                            # para operaciones gratuitas
                            operation_gratuita = invoice_line.product_id.list_price*invoice_line.quantity

                            if tax_id_obj.l10n_pe_edi_tax_code == '9996':
                                impuestosUnitarios['montoBaseImpuesto'] = operation_gratuita
                                impuestosUnitarios['montoTotalImpuestoUnitario'] = operation_gratuita*(18/100)
                                # cambio por los obs sunat
                                item['importeValorVentaItem'] = operation_gratuita
                            else:
                                impuestosUnitarios['montoBaseImpuesto'] = invoice_line.price_subtotal
                                impuestosUnitarios['montoTotalImpuestoUnitario'] = round(
                                    invoice_line.price_subtotal*tax_id_obj.amount/100, 2)

                            impuestosUnitarios['tasaImpuesto'] = tax_id_obj.amount
                            impuestosUnitarios['nombreImpuestoUnitario'] = tax_id_obj.description
                            impuestosUnitarios['montoSubTotalImpuestoUnitario'] = round(
                                invoice_line.price_subtotal*tax_id_obj.amount/100, 2)
                            
                            # GRATUITO
                            impuestosUnitarios['imp_trib_gratuito'] = operation_gratuita*(18/100)
                            #
                        else:
                            impuestosUnitarios['codigoImpuestoUnitario'] = tax_id_obj.l10n_pe_edi_tax_code
                            impuestosUnitarios['montoTotalImpuestoUnitario'] = tax_id_obj.amount*invoice_line.quantity
                            impuestosUnitarios['montoUnitario'] = tax_id_obj.amount
                        
                        # calculamos los montos de impuesto
                        if tax_id_obj.l10n_pe_edi_tax_code == '1000':
                            sum_gravada += invoice_line.price_subtotal
                        elif tax_id_obj.l10n_pe_edi_tax_code == '9997':
                            sum_exonerada += invoice_line.price_subtotal
                        elif tax_id_obj.l10n_pe_edi_tax_code == '9998':
                            sum_inafecta += invoice_line.price_subtotal
                        elif tax_id_obj.l10n_pe_edi_tax_code == '9996':
                            gratuito = True
                            sum_gratuitas += invoice_line.price_subtotal
                        elif tax_id_obj.l10n_pe_edi_tax_code == '9995':
                            sum_exportacion += invoice_line.price_subtotal
                        elif tax_id_obj.l10n_pe_edi_tax_code == '7152':
                            sum_imp_bolsa += tax_id_obj.amount*invoice_line.quantity
                    
                        lista_impuesto.append(impuestosUnitarios)

                    # Impuesto gratuito
                    imp_gratuito = 0.00
                    imp_trib_gratuito=0.00

                    if gratuito:
                    
                        data_invoice['gratuito'] = True
                        imp_gratuito = invoice_line.product_id.list_price*invoice_line.quantity
                        imp_trib_gratuito= imp_gratuito * (18/100)
                            
                    total_gratuitos+= imp_gratuito
                    total_tributos_gratuitos+= imp_trib_gratuito

                    item['imp_gratuito'] = imp_gratuito
                    #

                    item['impuestosUnitarios'] = lista_impuesto

                    item['indicadorDescuento'] = False
                    item['montoDescuento'] = 0.00
                    orden += 1
                    item['numeroOrden'] = orden

                    # Para el tag de precios unitarios
                    preciosUnitarios = {}
                    preciosUnitarios['codigoTipoPrecio'] = '01' if not gratuito else '02' # 02 si es gratuita
                    # if not tax_id_obj.price_include:
                    #    preciosUnitarios['montoPrecio'] = invoice_line.price_unit * \
                    #        (1+(tax_id_obj.amount/100))
                    #else:
                    #    preciosUnitarios['montoPrecio'] = invoice_line.price_unit

                    # unitario con igv
                    if not gratuito:
                        preciosUnitarios['montoPrecio'] = round((invoice_line.price_total - sum_imp_bolsa)/invoice_line.quantity,2)
                    else:
                        preciosUnitarios['montoPrecio'] = imp_gratuito
                    #
                    item['preciosUnitarios'] = preciosUnitarios

                    item['unidadMedida'] = invoice_line.product_uom_id.unit_measure_code

                    # precio unitario sin impuesto
                    # if tax_id_obj.price_include:
                    #    item['valorVentaUnitario'] = invoice_line.price_unit / \
                    #        (1+(tax_id_obj.amount/100))
                    # else:
                    #    item['valorVentaUnitario'] = invoice_line.price_unit
                    
                    # Remplazamos lo de arriba por esto
                    item['valorVentaUnitario'] = str(round(invoice_line.price_subtotal/invoice_line.quantity,5))

                    lista_items.append(item)
                elif not invoice_line.anticipo_id:
                    desct_global = True
                    amount_desct_global += invoice_line.price_subtotal
                else:
                    anticipo_obj = invoice_line.anticipo_id
                    data_invoice['deduccion'] = True
                    monto_anticipo = invoice_line.price_total
                    
                    totalAnticipo = totalAnticipo+monto_anticipo
                    subtotal_anticipos = subtotal_anticipos + invoice_line.price_subtotal
                    amount_tax = invoice_line.price_total -invoice_line.price_subtotal
                    impuesto_anticipos = impuesto_anticipos + amount_tax
                    
                    valor_venta_anticipo = invoice_line.price_subtotal
                    serie_anticipo, correlativo_anticipo = anticipo_obj.name.split('-')
                    cod_doc_anticipo = ''
                    if anticipo_obj.journal_id.sunat_document_type.code == "01":
                        cod_doc_anticipo = '02'
                    else:
                        cod_doc_anticipo = '03'
                    

                    dict_anticipo = {'codigoTipoDocumento': cod_doc_anticipo,
                                    'descripcion': invoice_line.name,
                                    'montoImporteValorVenta': abs(valor_venta_anticipo),
                                    'montoTotal': abs(monto_anticipo),
                                    'numeroCorrelativo': correlativo_anticipo,
                                    'serie': serie_anticipo
                                    }
                    list_anticipos.append(dict_anticipo)

        operacionesGratuitas = {}
        operacionesGratuitas['totalOperacionGratuito']=total_gratuitos
        operacionesGratuitas['totalTributoGratuito']=total_tributos_gratuitos
        data_invoice['operacionesGratuitas'] = operacionesGratuitas
        
        data_invoice['lista_items'] = lista_items

        data_invoice['lista_anticipos'] = list_anticipos

        # Valores para descuento Global
        data_invoice['tiene_desc_global'] = desct_global
        data_invoice['sum_total_desc'] = amount_desct_global*-1 if amount_desct_global != 0 else amount_desct_global

        # Se agrega lops Documentos Modificados
        data_invoice['rectificativa'] = False
        if invoice.move_type == "out_refund" or (invoice.move_type=="out_invoice" and invoice.journal_id.sunat_document_type.code == "08"):
            data_invoice['rectificativa'] = True
            serie_ref, correlativo_ref = invoice.related_document.split('-')
            data_invoice['codigoTipoNota'] = invoice.reason.code
            documentosModificados = {}
            documentosModificados['codigoTipoDocumento'] = invoice.related_document_type
            documentosModificados['fechaEmision'] = invoice.date_related_document.strftime('%Y-%m-%d')
            documentosModificados['serie'] = serie_ref
            documentosModificados['numeroCorrelativo'] = correlativo_ref
            data_invoice['documentosModificados'] = documentosModificados
            data_invoice['motivoNota'] = invoice.sustain

        # totales
        if type_identification_client.l10n_pe_vat_code == '1':
            data_invoice['razonSocialAdquiriente'] = ''
            data_invoice['nombresAdquiriente'] = client_obj.display_name
        else: 
            data_invoice['razonSocialAdquiriente'] = client_obj.display_name
            data_invoice['nombresAdquiriente'] = ''

        data_invoice['nombreComercialEmisor'] = company_partner_id.display_name
        data_invoice['numeroDocumentoIdentificacionAdquiriente'] = client_obj.vat
        data_invoice['razonSocialEmisor'] = company_partner_id.display_name
        data_invoice['telefonoEmisor'] = company_partner_id.phone

        # Dninaco Agregamos los datos de la orden de compra y documentos relacionados
        data_invoice['tieneOrden'] = True if invoice.codigo_compra else False
        data_invoice['ordenCompra'] = invoice.codigo_compra

        data_invoice['tieneDocumento'] = False
        data_invoice['documentos_relacionados'] = False
        documentos_relacionados = []
        if invoice.invoice_origin:
            
            stock_picking = self.env['stock.picking'].search([('origin', '=', invoice.invoice_origin)])
            if stock_picking:
                # documentos_relacionados = []
                for picking in stock_picking:
                    if picking.number_sunat:
                        data_invoice['tieneDocumento'] = True
                        
                        serie_g, correlativo_g = picking.number_sunat.split('-')
                        data_documento = {
                            'codigoTipoDocumento': '09', 
                            'numeroCorrelativo': correlativo_g,
                            'serie': serie_g
                        }
                        documentos_relacionados.append(data_documento)
                # data_invoice['documentos_relacionados'] = documentos_relacionados
        #
        # Evaluamos si asignaron documento relacionado
        if self.documentos:
            # documentos = []
            for documento in self.documentos:
                data_invoice['tieneDocumento'] = True    
                data_documento = {
                    'codigoTipoDocumento': documento.tipo.code, 
                    'numeroCorrelativo': documento.correlativo,
                    'serie': documento.serie
                }
                # documentos.append(data_documento)
                documentos_relacionados.append(data_documento)
            # data_invoice['documentos_relacionados'] = documentos
        #

        data_invoice['documentos_relacionados'] = documentos_relacionados


        # Dninaco agregamos estructura variable
        data_invoice['tieneEstructura'] = False
        data_invoice['estructuraVariable'] = False
        if True:
            data_invoice['tieneEstructura'] = True
            estructuras_variables = []

            # Estructura de vendedor
            data_estructura_vendedor = {
                'nombre': 'VENDEDOR_BSS', 
                'valor': invoice.invoice_user_id.name
            }
            estructuras_variables.append(data_estructura_vendedor)

            # Estructura de Tipo de Pago
            data_estructura_tipo_pago = {
                'nombre': 'TIPO_PAGO_BSS', 
                'valor': invoice.tipo_pago.description if invoice.tipo_pago else ''
            }
            estructuras_variables.append(data_estructura_tipo_pago)

            # Estructura de Forma de Pago
            data_estructura_forma_pago = {
                'nombre': 'FORMA_PAGO_BSS', 
                'valor': invoice.invoice_payment_term_id.name if invoice.invoice_payment_term_id else ''
            }
            estructuras_variables.append(data_estructura_forma_pago)

            # Estructura de Referencia
            data_estructura_referencia = {
                'nombre': 'REFERENCIA_BSS', 
                'valor': invoice.ref if invoice.ref else ''
            }
            estructuras_variables.append(data_estructura_referencia)

            
            data_invoice['estructuraVariable'] = estructuras_variables

        #

        # Dninaaco Agregamos tag observaciones
        data_invoice['observaciones'] = invoice.observaciones if invoice.observaciones else ''
        #

        data_invoice['baseDescuentoAntGravado'] = subtotal_anticipos
        data_invoice['descuentoAnticipoGravado'] = subtotal_anticipos
        #

        data_invoice['totalAnticipo'] = abs(totalAnticipo)
        data_invoice['totalIcbper'] = sum_imp_bolsa
        data_invoice['totalIgv'] = invoice.amount_tax 
        data_invoice['totalIsc'] = 0.00
        data_invoice['totalImpuesto'] = data_invoice['totalIgv'] + \
            data_invoice['totalIsc']
        data_invoice['totalPrecioVenta'] = invoice.amount_total + abs(totalAnticipo)
        data_invoice['totalValorVenta'] = invoice.amount_untaxed + abs(subtotal_anticipos)
        print("##sum_gravada#",sum_gravada)
        print("##amount_desct_global#",amount_desct_global)
        print("##subtotal_anticipos#",subtotal_anticipos)
        data_invoice['totalValorVentaOperacionesGravadas'] = (sum_gravada + amount_desct_global - abs(subtotal_anticipos)) if sum_gravada > 0 else sum_gravada
        data_invoice['totalValorVentaOperacionesExoneradas'] = sum_exonerada
        data_invoice['totalValorVentaOperacionesInafectas'] = sum_inafecta

        # if False:
        #    data_invoice['totalOperacionGratuito'] = 0.00
        #    data_invoice['totalTributoGratuito'] = 0.00
        if invoice.active_export_sale:
            data_invoice['totalOperacionExportacion'] = sum_exportacion

        # Agregamos los emails, cliente y contacto
        emails = ''
        if client_obj.email:
            emails = client_obj.email+","
        
        for contacto in client_obj.child_ids:
            if contacto.email:
                emails=emails+contacto.email+","

        data_invoice['correoElectronicoAdquiriente'] = emails
        data_invoice['ventaItinerante'] = 'false'

        # FORMA DE PAGO
        if not invoice.pago_credito:
            data_invoice['formaPago'] = 'CON'
            data_invoice['formaPago2'] = 'Contado'
        else:
            data_invoice['formaPago'] = 'CRE'
            data_invoice['formaPago2'] = 'Credito'

            listadoDeCuotas = []
            monto_total = 0.00
            for cuota in invoice.cuotas:
                monto_total = monto_total+round(cuota.amount,2)
                dict_data = {
                    'fechaVenPago': cuota.date.strftime('%Y-%m-%d'),
                    'montoPago': round(cuota.amount,2),
                    'nombre': cuota.name
                }
                listadoDeCuotas.append(dict_data)
            
            data_invoice['listadoDeCuotas'] = listadoDeCuotas
            data_invoice['montoNetoPenPago'] = monto_total
        #


        return data_invoice

    def build_dict_print_invoice(self):
        data_invoice = {}

        invoice = self

        company_obj = self.company_id
        company_partner_id = company_obj.partner_id

        journal_obj = self.journal_id


        data_invoice['pass_security'] = company_obj.pass_security
        data_invoice['codigoEmisor'] = company_obj.emisor_code
        data_invoice['number'] = invoice.name

        if invoice.move_type == 'out_refund':
            data_invoice['codigoTipoDocumento'] = journal_obj.sunat_document_type_related.code
        else:
            data_invoice['codigoTipoDocumento'] = journal_obj.sunat_document_type.code

        data_invoice['numeroDocumentoIdentificacionEmisor'] = company_partner_id.vat
        data_invoice['fechaEmision'] = invoice.invoice_date.strftime(
            '%Y-%m-%d')

        # SOPORTARA TODO TIPO DE DOCUMENTOS RELACIONADOS
		
        data_invoice['insertar_documentos']=False
        data_invoice['documentos']=[]
        
        if False:# self.documentos:
            data_invoice['insertar_documentos']=True
            lis_cadena_valores = []
            for documento in self.documentos:
                # DNINACO ESTO DE AQUI ES PARA VALIDAR SI ESTA ENVIADO REPETIDOS
                data_invoice['insertar_documentos']=True
                serie = documento.serie
                correlativo = int(documento.correlativo)
                codigo_doc = documento.tipo.codigo
                cadena_valores = serie+str(correlativo)+codigo_doc

                if cadena_valores in lis_cadena_valores:
                    raise UserError(_('Importante'), _("Esta enviando documentos repetidos, Favor de validar en Documentos Relacionados"))
                
                lis_cadena_valores.append(cadena_valores)

                # HASTA AQUI
                data_invoice['documentos'].append(documento)
                        
        #HASTA AQUI SE AGREGO PARA LA GUIA
        
        #APARTIR DE AQUI SE AGREGA EL CAMPO PARA ENVIAR TAG DE OBSERVACIONES
        data_invoice['observaciones']=self.narration
        #HASTA AQUI

        return data_invoice


    def export_invoice_validate(self):
        mensaje = ''
        client_obj = self.partner_id
        type_identification_client = client_obj.l10n_latam_identification_type_id

        if self.active_export_sale:
            if type_identification_client.l10n_pe_vat_code != '0':
                mensaje += '- Tipo de doc. de Cliente inválido.\n'

            for line_invoice in self.invoice_line_ids:
                if int(line_invoice.tax_ids.igv_affectation.code) != 40:
                    mensaje += '- Código de afectación de IGV inválido.\n'
                if line_invoice.tax_ids.amount != 0.0:
                    mensaje += '- Monto de IGV debe ser CERO.\n'
                    
            if len(mensaje) > 0:
                raise UserError(_(mensaje))	
        else:
            return True
        
    
    def cuotas_validate(self):
        mensaje = ''

        if self.pago_credito:
            if not self.cuotas:
                mensaje += '- Debe Registrar las Cuotas de pago.\n'

            amount = 0.00
            for cuota in self.cuotas:
                amount = amount + cuota.amount
            
            if self.amount_total < amount:
                mensaje += '- El monto total de las cuotas no cuadra con el total de factura.\n'


            if len(mensaje) > 0:
                raise UserError(_(mensaje))	
        else:
            return True
    

    def invoice_validate(self):
        mensaje = ''
        client_obj = self.partner_id
        type_identification_client = client_obj.l10n_latam_identification_type_id

        journal_obj = self.journal_id

        if type_identification_client.l10n_pe_vat_code == '1': # DNI
            if journal_obj.sunat_document_type.code == '01': # Factura
                mensaje += '- No puede emitir una Factura para un DNI.\n'
        if self.related_document_type:
            if self.related_document_type == '01': # Factura
                if False: #not 'F' in self.related_document and not journal_obj.is_contg:
                    mensaje += '- El documento relacionado debe ser serie F.\n'
            else: # Boleta
                if not 'B' in self.related_document and not journal_obj.is_contg:
                    mensaje += '- El documento relacionado debe ser serie B.\n'
            try:
                serie, correlativo = self.related_document.split('-')
                if len(serie) != 4:
                    mensaje += '- La serie del comprobante relacionado debe tener 4 caracteres.\n'
                if len(correlativo) != 8:
                    mensaje += '- El correlativo del comprobante relacionado debe tener 8 caracteres.\n'
            except:
                raise UserError(_('El comprobante relacionado no tiene formato valido xxxx-xxxxxxxx'))
                    
        if len(mensaje) > 0:
            raise UserError(_(mensaje))	
        else:
            return True
