# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.osv import osv
import xlsxwriter
from datetime import datetime, timedelta
import base64
from io import BytesIO
from odoo.tools.translate import _

workbook = None
fou = None
worksheet = None
header_style = None
header_body_style = None
body_style = None
date_style = None
hide_style = None
dn_company = ''
name_company = ''
period = ''
month_g = 0
year_g = 0


MONTHS = {  1: 'Enero',
            2: 'Febrero',
            3: 'Marzo',
            4:'Abril',
            5:'Mayo',
            6:'Junio',
            7:'Julio',
            8:'Agosto',
            9:'Septiembre',
            10:'Octubre',
            11:'Noviembre',
            12:'Diciembre',
    }


class StockMoveKardex(models.TransientModel):
    _name='report.kardex'
    
    kardex_file = fields.Binary('Download report')
    file_name = fields.Char('Kardex File')
    
    def _prepare_array_stock_move(self, sm, origin_des):
        sm_array = [sm, False, '', '', '', '', '', '', '', sm.id]
        to_code = None
        qty = sm.product_qty # Miguel
        picking = sm.picking_id
        
        if sm.date:
            #sm_array[1] = self.datetimeformat(sm.date)-timedelta(hours=5)
            sm_array[1] = sm.date-timedelta(hours=5)
        
        if picking:
            if not picking.related_doc:
                """
                FIXME: Tener en cuenta que este proceso solo se tendría que realizar al momento en el que se genere
                el stock_picking y no en la generación del kardex, ya que esto haría el proceso de generación del
                kardex más lento, solo por cuestiones de tiempo y autorización del funcional se invoca el método
                en este proceso.
                """
                picking._compute_tiene_doc_rel()
            
            tsn_arr = self._get_type_serie_number(picking)
            sm_array[2] = tsn_arr[0]
            sm_array[3] = tsn_arr[1]
            sm_array[4] = tsn_arr[2]
                 
            if picking.type_operation:
                to_code = picking.type_operation.code
                sm_array[5] = to_code
        else:
            """
            Si no tiene picking se asume que es un ajuste o un movimiento de fabricación y se obtiene 
            el código del ajuste o fabricación de su respectiva tabla
            """
            inventorys = self.env['stock.inventory'].search([('name', '=', sm.name[3:])])
            sm_array[5] = '99'

            if inventorys:
                if inventorys[0].beginning_balance:
                    sm_array[5] = '16'

                array_num = self._get_serie_number(inventorys[0].code or '**')
                sm_array[3] = array_num[0]
                sm_array[4] = array_num[1]
            else:
                # FIXME: Cuando se implemente el código a nivel de mrp se usará dicho campo para obtener
                #        la serie y correlativo, hasta entonces las líneas siguientes estarán comentadas.
                """
                manufacts = self.env['mrp.production'].search([('name', '=', sm.name)])
                if manufacts:
                    array_num = self._get_serie_number(manufacts[0].code or '**')
                    sm_array[3] = array_num[0]
                    sm_array[4] = array_num[1]
                else:
                    sm_array[4] = sm.name
                """
                if origin_des and sm.location_dest_id.usage == 'production':
                    sm_array[5] = '10'

                sm_array[4] = sm.name

            sm_array[2] = '00'
        
        if to_code and to_code == '05' or to_code == '06':
            if to_code == '05' and not origin_des:
                origin_des = True
                qty = qty*(-1)
            elif to_code == '06' and origin_des:
                origin_des = False
                qty = qty*(-1)
            
        if origin_des:
            sm_array[7] = qty
        else:
            sm_array[6] = qty                
        
        return sm_array
    
    def _get_type_serie_number(self, picking):
        invoice = picking.related_doc #doc_rel
        result = ['', '', '']
        
        if not invoice:
            """
            Si no se logra encontrar el comprobante relacionado, se asume que es una guía de remisión manual, tener en cuenta
            que cuando se desarrollo el kardex todavía no estaba habilitada la guía de remisión electrónica. Por lo que se
            sacará la información de campos específicos para guía de remisión.
            FIXME: Cuando se tenga todos los desarrollos completos se tendrá que modificar la lógica actual.
            """
            if not picking.number_sunat: #not picking.serie_guia_remision and not picking.correlativo_guia_remision:
                arr_s_n = self._get_serie_number(picking.origin)
                return ['31', arr_s_n[0], arr_s_n[1]]
            else:
                arr_s_n = self._get_serie_number(picking.number_sunat)
                return ['31', arr_s_n[0], arr_s_n[1]]
                #return ['31', (picking.serie_guia_remision or ''), (picking.correlativo_guia_remision or '')]
                
        journal = invoice.journal_id
        serie_number = False
        
        if journal:
            if journal.type in ['sale', 'sale_refund']:
                if journal.sunat_document_type and journal.sunat_document_type.code:
                    result[0] = journal.sunat_document_type.code
                
                serie_number = self._get_serie_number(invoice.name) #invoice.number
                
            elif journal.type in ['purchase', 'purchase_refund']:
                if invoice.type_voucher:
                    result[0] = invoice.type_voucher.code or '' 
                
                serie_number = self._get_serie_number(invoice.ref) #supplier_invoice_number
                
        if serie_number:
            result[1] = serie_number[0]
            result[2] = serie_number[1]
        
        return result
    
    def _get_serie_number(self, number):
        if not number:
            return ['','']
        
        idx = number.find('-')
        
        if idx == -1:
            return ['', number.strip()]
        
        return [number[0:idx].strip(), number[idx+1:].strip()]
    
    def _add_stock_move_array(self, stock_moves_dict, location, origin_des, product_id, sm):
        """
        @param stock_moves_dict: diccionario que contiene todas la ubicaciones, productos y movimientos.
        @param location: Ubicación del movimiento () 
        @param origin_des: Variable para diferencias si es un ingreso o salida de productos. True: Origen, False: Destino
        @param product_id: Objecto producto 
        @param sm: Objeto movimiento de mercadería
        """
        if location and stock_moves_dict.get(location.location_id.id):
            
            product_dict = stock_moves_dict.get(location.location_id.id)[1]
            
            if product_dict.get(product_id.id):
                product_dict.get(product_id.id)[1].append(self._prepare_array_stock_move(sm, origin_des))
            else:
                product_dict[product_id.id]= (product_id, [self._prepare_array_stock_move(sm, origin_des)])
    
    def generate_excel(self, year, month, warehouses, products, null_products):
        global dn_company
        global name_company
        global period
        global year_g
        global month_g
        
        stock_moves_dict = {}
        #args = []
        arg = ''
        locations = []
        
        if products:
            if len(products.ids)==1:
                arg='product_id = '+str(products.id)+' and '
            if len(products.ids)>1:
                arg='product_id in '+str(tuple(products.ids))+' and '

            #args.append(('product_id','in',map(lambda x: x.id, products)))
        ''' # Miguel
        if not warehouses:
            warehouses = self.env['stock.warehouse'].search([])
        '''
        location_pool = self.env['stock.location']
        
        for wh in warehouses:
            stock_moves_dict[wh.view_location_id.id] = (wh, {})
            locations += location_pool.search([('location_id', '=', wh.view_location_id.id)])
        
        if locations:
            locations_ids = map(lambda x:x.id, locations)
            ubicaciones=tuple(locations_ids)

        month = int(month)
        month_g = month
        year_g = year
        period =  MONTHS.get(month)+' '+str(year)
        #Creamos el filtro por periodo
        
        #args.append(('date', '>=', str(year)+'-'+str(month)+'-01 05:00:00'))
        date_ini = str(year)+'-'+str(month)+'-01 00:00:00'
        if month == 12:
            #args.append(('date', '<', str(year+1)+'-01'+'-01 05:00:00'))
            date_fin = str(year+1)+'-01'+'-01 00:00:00'
        else:
            #args.append(('date', '<', str(year)+'-'+str(month+1)+'-01 05:00:00'))
            date_fin = str(year)+'-'+str(month+1)+'-01 00:00:00'
        
        # Miguel: Cambio para optimizar el código y evitar el uso de sumar o restar horas por la Zona Horaria
        self._cr.execute("Select id from stock_move where "+arg+"(location_id in %s or location_dest_id in %s) and date at time zone 'utc' at time zone 'pet' >='"+str(date_ini)+"' and date at time zone 'utc' at time zone 'pet' < '"+str(date_fin)+"' and state in ('done')",(ubicaciones,ubicaciones))
        dict_resulset = self._cr.dictfetchall()
        
        move_ids = []
        for dic in dict_resulset:
            move_ids.append(dic.get('id'))

        stock_moves=self.env['stock.move'].search([('id','in',move_ids)])
        
        '''
        if not stock_moves:
            raise osv.except_osv(_('Error!'), _('No movements of products were found for the selected period.'))
        '''
        company = self.env['res.users'].browse(self._uid).company_id
        dn_company = company.vat
        name_company = company.name
        
        #Agrupamos los stock_moves almacén(warehouse) y por producto. 
        for sm in stock_moves:
            product_id = sm.product_id
            self._add_stock_move_array(stock_moves_dict, sm.location_id, True, product_id, sm)
            self._add_stock_move_array(stock_moves_dict, sm.location_dest_id, False, product_id, sm)
        
        for val in stock_moves_dict.values():
            for v in val[1].values():
                v[1].sort(key= lambda x: x[1], reverse=False) #cmp=None, key= lambda x: x[1], reverse=False
                
        self.generate_base_report()
                
        row = 4
        products_list_moves = []
        
        for loct_tupl in stock_moves_dict.values():
            for product_tupl in loct_tupl[1].values():                
                row = self._create_block(product_tupl, loct_tupl[0], row, True)
                products_list_moves.append(product_tupl[0].id) # Lista de productos con movimientos
                row+=2

        # Miguel: todos los productos o sólo algunos ingresados en el wizard
        if not products:
            # Miguel: Incluir en reporte Productos con saldos iguales a CERO?
            if null_products:
                prod_list_added = self.env['stock.init.kardex'].search([('warehouse_id','=', warehouses.id),('product_id', 'not in', products_list_moves),
                                                ('year', '=', year_g),('month', '=', month_g)])
            else:
                prod_list_added = self.env['stock.init.kardex'].search([('warehouse_id','=', warehouses.id),('product_id', 'not in', products_list_moves),
                                                ('year', '=', year_g),('month', '=', month_g),('stock_qty', '>', 0)])
        else:
            prod_list_added = self.env['stock.init.kardex'].search([('warehouse_id','=', warehouses.id),('product_id', 'in', products.ids),('product_id', 'not in', products_list_moves),
                                                ('year', '=', year_g),('month', '=', month_g)])

        # Miguel: cambio para incluir productos sin movimientos en el periodo
        unsorted_dic = {}
        if prod_list_added:
            for product in prod_list_added:
                unsorted_dic[product.product_id.default_code or ''] = product

            # Miguel: Ordenamos el diccionario tomando como criterio el campo 'default_code' del producto, 
            # con la finalidad de mostrarlo ordenado en el reporte.
            sorted_list = sorted(unsorted_dic.iteritems())
            for item in sorted_list:
                row = self._create_block(tuple(item[1].product_id), warehouses, row, False)
                row+=2
        #
        workbook.close()
        kardex_file = base64.encodestring(fou.getvalue())
        
        return self.create({'file_name': 'kardex.file.xlsx', 'kardex_file': kardex_file}) 
    
    def generate_base_report(self):
        global workbook
        global fou
        global worksheet
        global header_style
        global header_body_style
        global hide_style
        global body_style
        global date_style
        
        fou = BytesIO()
        workbook = xlsxwriter.Workbook(fou)
        worksheet = workbook.add_worksheet()
        worksheet.hide_gridlines(2)
        
        worksheet.set_column('A:A', 17)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 11)
        worksheet.set_column('D:D', 21)
        worksheet.set_column('E:E', 17)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 10)
        
        header_style = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'valign': 'top'})
        
        row = 0
        worksheet.write(row, 0, 'FORMATO 12.01: "REGISTRO DEL INVENTARIO PERMANENTE EN UNIDADES FÍSICAS - DETALLE DEL', header_style) 
        row+=1
        worksheet.write(row, 0, 'INVENTARIO PERMANENTE EN UNIDADES FÍSICAS"', header_style)
        row+=3
        
        header_style.set_font_size(11)
        
        header_body_style = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'font_size': 10,
            'valign': 'top',
            'border': 1})
        
        body_style = workbook.add_format({
            'font_size': 10,
            'text_wrap': True,
            'valign': 'top',
            'border': 1})
        
        hide_style = workbook.add_format({'font_color': 'white'})
        
        date_style = workbook.add_format({
            'font_size': 10,
            'text_wrap': True,
            'valign': 'top',
            'border': 1,
            'num_format': 'dd-mm-yyyy hh:mm:ss'})
    
    def dateformat(self, strdate):
        return datetime.strptime(strdate, "%Y-%m-%d ")
    
    def datetimeformat(self, strdate):
        return datetime.strptime(strdate, "%Y-%m-%d %H:%M:%S")
    
    def _create_block(self, product_tupl, warehouse, row, flag):
        global worksheet
        
        product = product_tupl[0]
        if flag:
            stock_move_arr = product_tupl[1]
        
        location_name = ''
        if warehouse.partner_id:
            location_name = (warehouse.partner_id.vat or '')+' '+(warehouse.partner_id.name or '')
        else:
            location_name = warehouse.name
        
        type_product = ''
        if product.type_existence:
            type_product = product.type_existence.code+' '+product.type_existence.description
        
        worksheet.write(row, 0, 'PERÍODO: '+ period, header_style); row+=1
        worksheet.write(row, 0, 'RUC: '+ dn_company, header_style); row+=1
        worksheet.write(row, 0, 'APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL: '+name_company, header_style); row+=1
        worksheet.write(row, 0, 'ESTABLECIMIENTO: '+ location_name, header_style); row+=1
        worksheet.write(row, 0, 'CÓDIGO DE LA EXISTENCIA: '+ (product.default_code or ''), header_style); row+=1
        worksheet.write(row, 0, 'TIPO (TABLA 5): '+ type_product, header_style); row+=1
        worksheet.write(row, 0, 'DESCRIPCIÓN: '+(product.name or ''), header_style); row+=1
        worksheet.write(row, 0, 'CÓDIGO DE LA UNIDAD DE MEDIDA (TABLA 6): '+ (product.uom_id and product.uom_id.kardex_code or ''), header_style); row+=2

        col=0
        
        worksheet.merge_range(row, col, row, col+3, 'DOCUMENTO DE TRASLADO, COMPROBANTE DE PAGO, DOCUMENTO INTERNO O SIMILAR', header_body_style); col+=4
        worksheet.merge_range(row, col, row+1, col, 'TIPO DE OPERACIÓN (TABLA 12)', header_body_style); col+=1
        worksheet.merge_range(row, col, row+1, col, 'ENTRADAS', header_body_style); col+=1
        worksheet.merge_range(row, col, row+1, col, 'SALIDAS', header_body_style); col+=1
        worksheet.merge_range(row, col, row+1, col, 'SALDO FINAL', header_body_style)
        row+=1
        col=0
        worksheet.write(row, col, 'FECHA', header_body_style); col+=1
        worksheet.write(row, col, 'TIPO (TABLA 10)', header_body_style); col+=1
        worksheet.write(row, col, 'SERIE', header_body_style); col+=1
        worksheet.write(row, col, 'NÚMERO', header_body_style); col+=1
        
        row+=1
        start_row = row+1
                
        #creamos la línea de saldo inicial.
        self._create_line_init(row, warehouse, product)
        row+=1
        
        #Bloque de movimientos
        if  flag:
            for sm_arr in stock_move_arr:
                self._create_line(sm_arr, row)
                row+=1
        
        #Totales
        self._create_line_totals(row, start_row, row)
        row+=1
        
        return row
        
    def _create_line(self, sm_arr, row):
        global worksheet
        col = 0
        if sm_arr[1]:
            worksheet.write_datetime(row, col, sm_arr[1], date_style)
        else:
            worksheet.write(row, col, '', body_style)
        col+=1 
        worksheet.write(row, col, sm_arr[2], body_style); col+=1
        worksheet.write(row, col, sm_arr[3], body_style); col+=1
        worksheet.write(row, col, sm_arr[4], body_style); col+=1
        worksheet.write(row, col, sm_arr[5], body_style); col+=1
        worksheet.write(row, col, sm_arr[6], body_style); col+=1
        worksheet.write(row, col, sm_arr[7], body_style); col+=1
        worksheet.write_formula(row, col, '=F'+str(row+1)+'-G'+str(row+1)+'+H'+str(row), body_style); col+=1
        #Este campo solo se debe mostrar para desarrollo, STOCK_MOVE-ID.
        #worksheet.write(row, col, sm_arr[9], hide_style)
        
    def _create_line_init(self, row, warehouse, product):
        global worksheet
        
        stk_init_obj = self.env['stock.init.kardex'].search([('warehouse_id','=', warehouse.id),('product_id', '=', product.id),
                                              ('year', '=', year_g),('month', '=', month_g)])
        stk_init_qty = 0
        
        if stk_init_obj:
            stk_init_qty = stk_init_obj.stock_qty
        
        worksheet.write(row, 1, '', body_style)
        worksheet.write(row, 3, 'SALDO INICIAL', body_style)
        worksheet.write(row, 5, stk_init_qty, body_style)
        worksheet.write_formula(row, 7, '=F'+str(row+1), body_style)
        
    def _create_line_totals(self, row, start_row, end_row):
        global worksheet
        
        worksheet.write(row, 4, 'TOTALES', header_body_style)
        worksheet.write_formula(row, 5, '=SUM(F'+str(start_row)+':F'+str(end_row)+')', body_style)
        worksheet.write_formula(row, 6, '=SUM(G'+str(start_row)+':G'+str(end_row)+')', body_style)
    
    
    