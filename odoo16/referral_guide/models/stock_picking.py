# -*- coding: utf-8 -*-

from odoo.osv import osv,expression
from .commons import *
from lxml import etree, objectify
from odoo import fields, models, api, _
from odoo.exceptions import Warning
from .except_error import WebServiceError
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
import pytz
from pytz import timezone

JOURNAL_TYPE_MAP = {
    ('outgoing', 'customer'): ['sale'],
    ('outgoing', 'supplier'): ['purchase_refund'],
    ('outgoing', 'transit'): ['sale', 'purchase_refund'],
    ('incoming', 'supplier'): ['purchase'],
    ('incoming', 'customer'): ['sale_refund'],
    ('incoming', 'transit'): ['purchase', 'sale_refund'],
}

class stock_picking(models.Model):
    _inherit = "stock.picking"

    referencia = fields.Char('Referencia')
    orden_compra = fields.Char('Orden de Compra')

    @api.onchange('fecha_traslado')
    def onchange_date(self):
        if self.fecha_traslado and  datetime.strptime(str(self.fecha_traslado), DEFAULT_SERVER_DATE_FORMAT).date() < datetime.now().date():
            self.fecha_traslado = False
            self.fecha_traslado_valida = True
        else:
            self.fecha_traslado_valida = False
    
    def get_fecha(self,fecha):
        """
			Función que retorna un datetime con la zona horaria del partner asociado al comprobante,
			recibe un string
		"""
        tz = 'America/Lima'
        if self.partner_id and self.partner_id.tz:
            tz = self.partner_id.tz
        #fecha_datetime_obj = datetime.strptime(fecha, DEFAULT_SERVER_DATETIME_FORMAT)
        fecha_utc_timezone = timezone('UTC').localize(fecha) #fecha_datetime_obj
        fecha_conv = fecha_utc_timezone.astimezone(timezone(tz))
        return fecha_conv
    
    @api.onchange('num_doc_rel_cd')
    def _onchange_num_doc_rel_cd(self):
        patternDni="^[0-9]{4}-[0-9]{2}-[0-9]{3}-[0-9]{6}$"      
        
        if self.num_doc_rel_cd and re.match(patternDni,self.num_doc_rel_cd)==None:
            raise ValidationError(_("La Numeración DAM es un valor numérico de la forma XXXX-XX-XXX-XXXXXX"))
    
    @api.onchange('transfer_reason')
    def _onchange_motivo_traslado(self):
        for stock_picking in self:
            if stock_picking.transfer_reason.code == '09':
                catalogo_21_obj = self.env['peb.catalogue.21'].search([('code','=','01'),('description','=','NUMERACION DAM')])
                stock_picking.cod_num_doc_rel_cd = catalogo_21_obj.id if catalogo_21_obj else False
            else:
                stock_picking.num_doc_rel_cd  = stock_picking.cod_num_doc_rel_cd = False
    
    @api.onchange('doc_number_conveyor')
    def _onchange_doc_number_conveyor(self):
        if self.type_doc_conveyor and self.type_doc_conveyor.l10n_pe_vat_code == '6' and self.doc_number_conveyor:
            self.validate_ruc(self.doc_number_conveyor)            

        elif self.type_doc_conveyor and self.type_doc_conveyor.l10n_pe_vat_code == '1' and self.doc_number_conveyor:
            self.is_numero(self.doc_number_conveyor)
    
    @api.onchange('type_doc_conveyor')
    def _onchange_type_doc_conveyor(self):
        self.doc_number_conveyor = False
    
    @api.model
    def is_numero(self,dni):
        patternDni="^[0-9]{8}$"        
        
        if re.match(patternDni,dni)==None:           
            raise ValidationError(_("The DNI it's an 8 digit numerical value."))
    
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
    
    def button_generate_despatch(self):
        self.write({})

        # AGREGAMOS VALIDACIÓN
        if self.peso_total<=0:
            raise ValidationError(_("Debe rellenar el campo Peso Total Kg Mayor a 0"))
        #
        
        res = {}
        dict = self.valida_doc()
        valido = dict.get('valido', False)
        message = dict.get('message', '')
        if not valido:
            """            
            return {
                    'type': 'ir.actions.client',
                    'tag': 'action_warn',
                    'name': 'Warning',
                    'params': {
                           'title': 'Advertencia',
                           'text': _(message),
                           'sticky': False
                        }
                }            
            """
            #return {'warning':{'title':'warning','message':message}}
            raise ValidationError(_(message))
        else:
            if not self.number_sunat:
                self.obtener_sec()
            
            if not self.shipping_status_sunat:
                self.actualizar_estado_sunat(self.id, ESTADOS_ENVIO_SUNAT['ENVIADO'])
            
            return self.enviar_guia_remision()

    def button_print_despatch(self):
        assert len(self) == 1, 'Esta opción solo debe ser usada en un solo momento.'
            
        resp = self.solicitar_pdf_ebis(WS['IMPRESION'])
        
        resp = objectify.fromstring(resp.encode('utf-8'))

        # Siempre traera el xml
        filecontent = False
        filecontent_xml = False
        extension = '.pdf'
        extension_xml = '.xml'
        
        filecontent = get_tag_text(resp, TAGS['PDF'])
        filecontent_xml = get_tag_text(resp, TAGS['XML'])
        
        
        if (filecontent) :
            file_id = self.env['impresion'].create({'file_id': filecontent})
            filename_field = get_pdf_filename(self.construir_dict(WS['IMPRESION']))

            self.write({
                        'field_pdf': filename_field+extension,
                        'file_data': filecontent,
                        'field_xml': filename_field+extension_xml,
                        'file_data_xml': filecontent_xml,
                        'not_active_get_print_guia': True
                        })
            """
            if (file_id and file_id.id != False) :
                return {
                          'res_model': 'ir.actions.act_url',
                          'type'     : 'ir.actions.act_url',
                          'target'   : 'self',
                          'url'      : '/descarga/pdf?model=impresion&field=file_id&id=' + str(file_id.id) + '&filename_field=' + filename_field + '.pdf',
                       }
            """
        else:
            raise UserError(_("Documento no encontrado"))
    
    def button_listado_logs(self):
        """
            Método que abre una nueva ventana que contiene 
            los LOGS de un documento
        """
        mod_obj = self.env['ir.model.data']
        
        view_ref = mod_obj.check_object_reference('referral_guide', 'logs_guia_remision_tree_view')
        view_id = view_ref and view_ref[1] or False
        
        id_activo = self.id
        
        logs_ids = []
        for so in self.env['logs.guia.remision'].search([('guia_remision_id', '=', id_activo)]):
            logs_ids += [so.id]
        domain = "[('id','in',[" + ','.join(map(str, logs_ids)) + "])]"
        
        return {
                'type': 'ir.actions.act_window',
                'name':"Listado Logs",
                'view_mode': 'tree',
                #'view_type': 'tree',
                'view_id': view_id,
                'res_model': 'logs.guia.remision',
                'target': 'new',
                'domain': domain,
                'context': {}
        }
    
    def solicitar_pdf_ebis(self, tipo):
        """
            Método que solicita el archivo PDF y si lo obtiene 
            descarga el documento obtenido.
            :param diccionario tipo: Tipo de diccionario que se debe generar para la petición 
        """
        try:
            metodo = self.env['ir.config_parameter'].search([('key', '=', WS[tipo])]).value
            
            dict = self.construir_dict(WS[tipo])
            
            #trama = get_trama_imprimir_cpe_pago(dict, metodo, False) 
            #DNINACO SE LE ENVIA EL SELF PAR ABTENER LA PSS DE SEGURIDAD
            trama = get_trama_imprimir_cpe_pago(dict, metodo,self)                                                 
        
            url = self.env['ir.config_parameter'].search([('key', '=', WS['URL_COMPROBANTE'])]).value
        
            respuesta = get_respuesta_zeep(url, metodo, trama)
        except Exception as e:
            raise UserError('WebService Error',
                _("Comunicarse con el Adminstrador del Sistema - '%s'") % _(e,))
        return respuesta

    def enviar_guia_remision(self):
        metodo = self.env['ir.config_parameter'].search([('key', '=', WS['COMPROBANTE_PAGO'])]).value
        dict = self.construir_dict(WS['COMPROBANTE_PAGO'])
        #se envia el self DNINACO
        trama = get_trama_guia_remision(dict, metodo,self)
        url = self.env['ir.config_parameter'].search([('key', '=', WS['URL_COMPROBANTE'])]).value
        try:
            respuesta = get_respuesta_zeep(url, metodo, trama)
        except WebServiceError as e:
            if e.args[0][0] == 111:
                self.actualizar_estado_sunat(self.id, ESTADOS_ENVIO_SUNAT['POR_ENVIAR'], _('No se puedo realizar la comunicación con el Sistema Ebis. - ') + _(e.args[0][0]))
            elif e.args[0] == "''":
                self.actualizar_estado_sunat(self.id, ESTADOS_ENVIO_SUNAT['ENVIADO'], _('El Sistema EBIS sufrió una caida inesperada.'))
                return self.env['mensaje.emergente'].get_mensaje('WebServiceError', _('Se perdió la conexión'), False)
            else:
                self.actualizar_estado_sunat(self.id, ESTADOS_ENVIO_SUNAT['ENVIADO'])
            return self.env['mensaje.emergente'].get_mensaje('WebServiceError', e.args[0][0], e.args[0][0])
        
        return self.recibir_comprobante_pago_respuesta(respuesta)
    
    def valida_doc(self):
        valido = True
        message = ''
        
        if not self.company_id.emisor_code:
            message += '- Código Emisor.\n'
        if not self.company_id.country_id:
            message += '- País (Empresa).\n'
        if not self.company_id.state_id:
            message += '- Departamento (Empresa).\n'
        if not self.company_id.city_id:
            message += '- Provincia (Empresa).\n'
        if not self.company_id.district_id:
            message += '- Distrito (Empresa).\n'
        if not self.company_id.street: #VALIDAR
            message += '- Dirección (Empresa).\n'
        """
        if not self.related_doc:
            valido = False
            message += '- Documento Relacionado.\n'
        else:
        """
        if self.related_doc: #not
            if not self.related_doc.shipping_status_sunat:
                message += '- Enviar Comprobante de Venta a SUNAT.\n'
            elif self.related_doc.shipping_status_sunat.code not in [ESTADOS_ENVIO_SUNAT['ACEPTADO_EBIS'], ESTADOS_ENVIO_SUNAT['ACEPTADO_SUNAT'], ESTADOS_ENVIO_SUNAT['ACEPTADO_SUNAT_OBS.']]:
                message += '- Comprobante de Venta en estado Aceptado EBIS, Aceptado SUNAT o Aceptado SUNAT con Obs.\n'
            
        if not self.partner_id.state_id:
            message += '- Departamento (Cliente).\n'
        if not self.partner_id.city_id:
            message += '- Provincia (Cliente).\n'
        if not self.partner_id.l10n_pe_district:
            message += '- Distrito (Cliente).\n'
        if not self.partner_id.street:
            message += '- Dirección (Cliente).\n'
        
        if not self.transfer_reason:
            message += '- Motivo de Traslado.\n'
        
        if not self.type_conveyor:
            message += '- Tipo de Transporte.\n'
        else:
            # if not self.type_doc_conveyor:
                #message += '- Tipo de Documento.\n'
            # if not self.doc_number_conveyor:
                #message += '- Número de Documento.\n'
            # if self.type_conveyor.code == '01':
                # if not self.name_conveyor:
                    #message += '- Nombre o Razón Social.\n'
            # else:
            #    if not self.register_car_number:
            #        message += '- Número de placa.\n'
            if not self.shipping_carrier_id:
                message += '- Seleccione Transportista.\n'

            if not self.type_conveyor.code == '01':
                if not self.vehicle_id:
                   message += '- Número de placa.\n'
                
                
        if not self.ind_transb_prog:
            message += '- Indicador Transbordo Progamado.'
        
        if len(message)>0:
            valido = False
            message = 'Se requiere:\n' + message
            
        dict = {'valido' : valido,
                'message': message,
                }
        return dict

    def construir_dict(self, func):
        dict = {}
        #date_sp = self.date.strftime(DEFAULT_SERVER_DATETIME_FORMAT) #MIGUEL
        #date_done_sp = self.date_done.strftime(DEFAULT_SERVER_DATETIME_FORMAT) #MIGUEL
        #
        date_picking = self.get_fecha(self.date).strftime('%Y-%m-%d %H:%M:%S')
        date_sp = self.fecha_emision_guia.strftime('%Y-%m-%d') if self.fecha_emision_guia else date_picking[:date_picking.find(" ")]
        if (func == WS['IMPRESION']) :
            
            company = self.company_id
            dict = {'codigo_emisor' : company.emisor_code,
                'number' : self.number_sunat,
                'tipo_documento' : '09',
                'numerodocumento' : company.vat,
                'date_invoice' : date_sp, }
        else:
            serie, correlativo = self.number_sunat.split('-')
            
            dict['serie_documento'] = serie
            dict['numero_documento'] = correlativo
            #dict['fecha_emision'] = date_sp[:date_sp.find(" ")] #self.date[:self.date.find(" ")]
            self.fecha_emision_guia = datetime.now(timezone('America/Lima')).date()
            dict['fecha_emision'] = self.fecha_emision_guia.strftime('%Y-%m-%d')
            #

            # AGREGAMOS NUEVOS TAGS DE HORA
            hora = datetime.now(timezone('America/Lima')).time().strftime('%H:%M:%S')
            dict['horaEmision'] = hora
            #

            dict['tipo_documento'] = '09'
            dict['observaciones'] = self.observaciones
            
            if self.related_doc:
                dict['doc_rel_numero'] = self.related_doc.name
                dict['doc_rel_tipo'] = self.related_doc.journal_id.sunat_document_type.code #self.env['peb.catalogue.21'].search([('description','=','OTROS')]).code

                # AGREGAMOS NUEVOS TAGS DOC RELACIONADO
                dict['descripcion'] = 'FACTURA' if dict['doc_rel_tipo']=='01' else 'BOLETA'
                dict['codTipDocEmisor'] = '6'
                dict['rucEmisor'] = self.company_id.vat
                #
          
            dict['remit_cod'] = self.company_id.emisor_code
            dict['remit_nombre'] = self.company_id.name
            dict['remit_num_doc'] = self.company_id.vat
            dict['remit_tipo_doc'] = self.company_id.identification_type_id.l10n_pe_vat_code
            
            dict['dest_nombre'] = self.partner_id.name
            dict['dest_num_doc'] = self.partner_id.vat
            dict['dest_tipo_doc'] = self.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code
            
            """
            dict['estab_ter_nombre'] = ''
            dict['estab_ter_num_doc'] = ''
            dict['estab_ter_tipo_doc'] = ''
            """
            
            dict['cod_motivo'] = self.transfer_reason.code
            dict['descripcion'] = self.transfer_reason.description
            dict['ind_trans_prog'] = self.ind_transb_prog
            dict['num_doc_rel_cd'] = self.num_doc_rel_cd
            dict['cod_num_doc_rel_cd'] = self.cod_num_doc_rel_cd.code
            
            '''DNINACO -- SE MODIFICO PARA QUE EL VALOR SEA ENVIADO EN KGM Y NO EN KG'''
            dict['unid_med_peso_bruto'] = 'KGM'
            
            dict['cod_mod_traslado'] = self.type_conveyor.code
            dict['fecha_ini_traslado'] = self.fecha_traslado.strftime('%Y-%m-%d')
            
            if self.type_conveyor.code == '01':
                dict['type_conveyor'] = 'publico'
            else:
                dict['type_conveyor'] = 'privado'
            
            if self.type_conveyor.code == '01':
                dict['trans_pub_num_ruc'] = self.vat_name
                dict['trans_pub_tipo_doc'] = self.shipping_carrier_id.l10n_latam_identification_type_id.l10n_pe_vat_code
                dict['trans_pub_nombre'] = self.shipping_carrier_id.names
            elif self.type_conveyor.code == '02':
                #MIGUEL:
                dict['trans_pub_nombre'] = self.shipping_carrier_id.names
                dict['trans_pri_placa'] = self.vehicle_id.plate_number                
                dict['trans_pri_con_num_doc'] = self.vat_name
                dict['trans_pub_tipo_doc'] = self.shipping_carrier_id.l10n_latam_identification_type_id.l10n_pe_vat_code
                dict['trans_pub_nombre'] = self.shipping_carrier_id.names

                # AGREGAMOS NUEVOS TAGS DATOS DE TRANSPORTE
                dict['apellidosTransprt'] = self.shipping_carrier_id.last_name if self.shipping_carrier_id.last_name else ''
                dict['numLicenciaConduct'] = self.shipping_carrier_id.function if self.shipping_carrier_id.function else ''
                #
            
            partner = self.partner_id
            #direccion_multi = self.direccion_entrega
            direccion_multi = None
            
            '''DNINACO AGREGARDO PARA MULTI DIRECCIONES DE LLEGADA PARA LA GUÍA DE REMISIÓN'''
            if not direccion_multi:
                dict['dir_lleg_ubigeo'] = partner.l10n_pe_district.code
                dict['dir_lleg_direccion'] = partner.street
                dict['departamento_adq'] =  partner.state_id.name
                dict['distrito_adq'] = partner.l10n_pe_district.name
                dict['provincia_adq'] = partner.city_id.name

                # AGREGAMOS NUEVOS TAGS
                dict['longitud'] = ''
                dict['latitud'] = ''
                if self.transfer_reason.code=='04':
                    dest = self.env['stock.warehouse'].search([('partner_id', '=', self.partner_id.id)])
                    dict['rucAsociado_adq'] = self.company_id.vat
                    dict['codigoSunatAnexo_adq'] = dest.warehouse_annex_code
                else:
                    dict['rucAsociado_adq'] = ''
                    dict['codigoSunatAnexo_adq'] = ''
                #

            else:
                dict['dir_lleg_ubigeo'] = direccion_multi.departamento_id.codigo + direccion_multi.provincia_id.codigo + direccion_multi.distrito_id.codigo
                dict['dir_lleg_direccion'] = direccion_multi.street
                dict['departamento_adq'] =  direccion_multi.departamento_id.name
                dict['distrito_adq'] = direccion_multi.distrito_id.name
                dict['provincia_adq'] = direccion_multi.provincia_id.name
            
            company = self.company_id
            dict['pto_part_ubigeo'] = company.district_id.code
            dict['pto_part_direccion'] = company.street
            dict['departamento_emi'] =  company.state_id.name
            dict['distrito_emi'] = company.district_id.name
            dict['provincia_emi'] = company.city_id.name

            # AGREGAMOS NUEVOS TAGS
            if self.transfer_reason.code=='04':
                dict['rucAsociado_emi'] = self.company_id.vat
                dict['codigoSunatAnexo_emi'] = '0000' #self.picking_type_id.warehouse_id.warehouse_annex_code
            else:
                dict['rucAsociado_emi'] = ''
                dict['codigoSunatAnexo_emi'] = ''
            #
            
            """
            dict['num_contenedor'] = ''
            
            dict['cod_puerto'] = ''
            """
            
            obj_stock_move = self.env['stock.move'].search([('picking_id', '=', self.id), ('company_id', '=', self.company_id.id)])
            
            items = etree.Element('lst')
            orden = 1
            num_bultos = 0
            peso_bruto_tot = 0.00
            for item in obj_stock_move:
                
                peso_bruto_tot += item.product_qty * item.product_id.product_tmpl_id.weight
                tieneEstructura = True
                estructuras_variables = []
                if tieneEstructura:
                    # Estructura de vendedor
                    # recoremos los lotes
                    name_lote=''
                    for lot_id in item.move_line_ids.lot_id:
                        
                        if name_lote != '':
                            name_lote = name_lote+","

                        name_lote = name_lote+lot_id.name

                    data_estructura_serie_lote = {
                        'nombre': 'SERIE_LOTE_BSS', 
                        'valor': name_lote
                    }
                    estructuras_variables.append(data_estructura_serie_lote)

                dict_item = {'cantidad' : str(item.product_uom_qty), #Miguel: int(item.product_qty)
                            'descripcion' : item.product_id.name,
                            'item' : item.product_id.default_code or item.product_id.id, #Miguel: item.product_id.id
                            'num_orden' : orden,
                            'unidad_medida' : item.product_uom.unit_measure_code,
                            #
                            'tieneEstructura': tieneEstructura,
                            'estructuraVariable': estructuras_variables,
                            #
                            'lst_items' : '',
                            'peso_total_item': item.product_qty * item.product_id.product_tmpl_id.weight,
                            }
                num_bultos += int(item.product_qty) #Miguel: dict_item['cantidad']
                get_datos_items_guia(dict_item)
                item = dict_item.get('lst_items', False)
                if item:
                    items.append(item)
                orden += 1
            
            almacen_inicio = self.picking_type_id.warehouse_id.partner_id
            cod_ubigeo_partida =almacen_inicio.l10n_pe_district.code or almacen_inicio.district_id.code
            direccion_partida =almacen_inicio.street      
                        
            dir_partida = etree.Element('dir_partida')
            
            if self.transfer_reason.code =='04':
            
                dict_direccion_partida = {'codigoUbigeo': cod_ubigeo_partida,
                                'direccionDetallada':direccion_partida,
                                'rucAsociado':self.company_id.vat,
                                'codigoSunatAnexo':self.picking_type_id.warehouse_id.warehouse_annex_code,
                                'direc_partida':'',
                    }
            else:
                dict_direccion_partida = {'codigoUbigeo': cod_ubigeo_partida,
                                'direccionDetallada':direccion_partida,
                                'rucAsociado': '',
                                'codigoSunatAnexo': '',
                                'direc_partida':'',
                    }
            
            get_direccion_partida(dict_direccion_partida)
            
            direccion_partida_tag = dict_direccion_partida.get('direc_partida', False)
            
            if direccion_partida_tag:
                dir_partida.append(direccion_partida_tag)
            
            dict['num_bultos'] = str(num_bultos).zfill(11)
            # dict['peso_bruto_total'] = peso_bruto_tot
            dict['peso_bruto_total'] = self.peso_total
            dict['items'] = items
            dict['dataDirecPartida'] = dir_partida

            # Dninaco agregamos estructura variable
            dict['tieneEstructura'] = False
            dict['estructuraVariable'] = False
            if True:
                dict['tieneEstructura'] = True
                estructuras_variables = []

                # Estructura de Orden Compra
                data_estructura_orden_compra = {
                    'nombre': 'ORDEN_COMPRA_BSS', 
                    'valor': self.orden_compra if self.orden_compra else ''
                }
                estructuras_variables.append(data_estructura_orden_compra)

                # Estructura de Referencia
                data_estructura_referencia = {
                    'nombre': 'REFERENCIA_BSS', 
                    'valor': self.referencia if self.referencia else ''
                }
                estructuras_variables.append(data_estructura_referencia)

                
                dict['estructuraVariable'] = estructuras_variables

            #

        return dict

    def actualizar_estado_sunat(self, id_comprobante, estado_final, descripcion_detallada=None):
        """
            Método que actualiza el estado del comprobante,
            y registra el respectiv log de la actualización.
            :param int id_comprobante : id del comprobante
            :param int estado_final : codigo del estado final
        """
        obj_estado_inicial = self.search([('id', '=', id_comprobante), ('company_id', '=', self.company_id.id)]).shipping_status_sunat
        obj_estado_final = self.env['peb.shipping.status.sunat'].search([('code', '=', estado_final)])
        
        values = {}
        values['guia_remision_id'] = id_comprobante
        values['fecha'] = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        
        if obj_estado_final and obj_estado_inicial.id:
            values['estado_ini'] = obj_estado_inicial.name
            
        values['descripcion'] = obj_estado_final.description
        values['estado_fin'] = obj_estado_final.name
        
        if descripcion_detallada != None:
            values['descripcion_detallada'] = descripcion_detallada
        
        # Se registran los datos en la tabla de logs
        self.env['logs.guia.remision'].create(values)
        
        obj_comprobante = self.search([('id', '=', id_comprobante), ('company_id', '=', self.company_id.id)])
        obj_comprobante.write({'shipping_status_sunat': obj_estado_final.id})

    def recibir_comprobante_pago_respuesta(self, rpta):
        """
            Método que procesa la respuesta obtenida 
            al realizar una petición y 
            muestra los datos procesadsos. (str)
        """
        mod_obj = self.env['ir.model.data']
        view_ref = mod_obj.check_object_reference('referral_guide', 'recibir_comprobante_pago_respuesta_view')
        view_id = view_ref and view_ref[1] or False
        
        rpta_obj_xml = objectify.fromstring(rpta.encode('utf-8'))
        
        codigo_estado = get_tag_text(rpta_obj_xml, TAGS['COD_EST']) or ''
        observaciones = get_tag_text(rpta_obj_xml, TAGS['OBS']) or ''
        descripcion_estado = get_tag_text(rpta_obj_xml, TAGS['DESC_EST']) or ''
        
        if codigo_estado == INDICADOR_RESULTADO['INFO']:
            self.actualizar_estado_sunat(self.id, ESTADOS_ENVIO_SUNAT['ACEPTADO_EBIS'], observaciones)
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
        self.status_sunat_code = self.shipping_status_sunat.code
    
    @api.depends('type_conveyor')
    def _compute_tipo_transp(self):
        for stock_picking in self:
            if stock_picking.type_conveyor:
                stock_picking.code_type_conveyor = stock_picking.type_conveyor.code
            else:
                stock_picking.code_type_conveyor = False

    @api.depends('transfer_reason')
    def _compute_motivo_traslado(self):
        for stock_picking in self:
            if stock_picking.transfer_reason:
                stock_picking.cod_transfer_reason = stock_picking.transfer_reason.code
            else:
                stock_picking.cod_transfer_reason = False
    
    @api.depends('origin')
    def _compute_tiene_doc_rel(self):
        self.write({})
        for stock_picking in self:
            if stock_picking.origin:
                if not stock_picking.related_doc:
                    obj_doc_rel = stock_picking.get_doc_rel()
                    if obj_doc_rel:
                        stock_picking.has_related_doc = True
                        stock_picking.write({'related_doc': obj_doc_rel.id})
                    else:
                        stock_picking.has_related_doc = False
                else:
                    stock_picking.has_related_doc = True
            else:
                stock_picking.has_related_doc = False

    def obtener_sec(self):
        sequence_obj = self.env['ir.sequence'].search([('code','=', 'guia_remitente_codigo'), ('company_id', '=', self.company_id.id),('warehouse_id','=',self.picking_type_id.warehouse_id.id)])
        if not sequence_obj:
            raise osv.except_osv(_('Comunicarse con el Administrador'),_("No existe una secuencia asociada para Guías de Remisión Remitente, Ejem. 'TXXX-' "))
        #serie_correlativo = self.pool.get('ir.sequence').get_id(self._cr, self._uid, sequence_id, 'id', context=self._context)
        serie_correlativo = self.pool.get('ir.sequence').get_id(sequence_obj,sequence_obj.id)
        self.number_sunat = serie_correlativo

    def get_doc_rel(self):
        if self.origin:
            """
            Se realiza la modificación para que se obtenga el comprobante relacionado directamente desde
            el origen del picking, ya que actualmente solo está que lo trae para el proceso de ventas.
            El origin del picking y del invoice son iguales para el proceso de Ventas (desde ventas y POS) y
            para el proceso de compras. Para los otros procesos (Inventario o creación directa no tiene
            asociado un invoice).
            """
            def _get_invoces(origin):
                return self.env['account.move'].search([('invoice_origin', '=', origin), ('company_id', '=', self.company_id.id)],limit=10)
                
            #obj_sale_order = self.env['sale.order'].search([('name','=', self.origin), ('company_id', '=', self.company_id.id)],limit=1)
            invoices = _get_invoces(self.origin)
            if not invoices and self.name:
                """
                Realizamos la búsqueda por nombre del picking, esto se cumple para la creación de las notas de créditos,
                Esto solo funcionaría cuando la nota de crédito se crea a partir de la reversión de un movimiento de mercadería.
                """
                invoices = _get_invoces(self.name)
            
            if invoices:
                """
                Tener en cuenta que una venta que genera el picking puede tener asociado varios invoices,  
                en esta caso solo retornamos el primero. FIXME Investigar este caso para el formato kardex
                sunat, cual debería mostrarse.
                """
                return invoices[0]
            
            return None
    

    shipping_status_sunat = fields.Many2one('peb.shipping.status.sunat', string="Estado Sunat", readonly=True, copy=False)
    status_sunat_code = fields.Char(compute='_compute_estado_envio_sunat', copy=False)

    related_doc = fields.Many2one('account.move', string='Documento Relacionado', copy=False)
    number_sunat = fields.Char('Número Documento', copy=False)
    
    transfer_reason = fields.Many2one('peb.catalogue.20', string="Motivo de Traslado")
    ind_transb_prog = fields.Selection([('s','Sí'),('n','No')],string='Indicador de Transbordo Programado')
    cod_transfer_reason = fields.Char(compute="_compute_motivo_traslado")
    cod_num_doc_rel_cd = fields.Many2one('peb.catalogue.21', string="Tipo Documento Relacionado")
    num_doc_rel_cd = fields.Char('Numeración DAM', copy=False)
    fecha_traslado= fields.Date('Fecha de Traslado', copy=False)
    fecha_traslado_valida = fields.Boolean('Fecha de traslado valida', default=False, copy=False)
    fecha_emision_guia = fields.Date('Fecha Guía Remisión', copy=False)
    
    code_type_conveyor = fields.Char('Codigo tipo Trans.',compute="_compute_tipo_transp")
    type_conveyor = fields.Many2one('peb.catalogue.18',string="Tipo de Transporte")
    type_doc_conveyor = fields.Many2one('l10n_latam.identification.type',string="Tipo de Documento")
    
    doc_number_conveyor = fields.Char('Número de Documento',size=11)
    name_conveyor = fields.Char('Nombre o Razón Social')    
    register_car_number = fields.Char('Número de placa',size=8)  
    has_related_doc = fields.Boolean(String='Tiene documento relacionado?', compute="_compute_tiene_doc_rel", copy=False)    
    serie_referral_guide = fields.Char('Serie Guía Remisión', size=4)
    correlative_referral_guide = fields.Char('Correlativo Guía Remisión', size=8)    
    
    field_pdf = fields.Char('Name Pdf',  copy=False)
    file_data = fields.Binary('Rep. Impresa',  copy=False)    
    field_xml = fields.Char('Name Xml',  copy=False)
    file_data_xml = fields.Binary('XML',  copy=False)    
    not_active_get_print_guia = fields.Boolean('Active Invoice Print',  copy=False)
