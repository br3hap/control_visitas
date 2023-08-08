# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.osv import osv
from odoo.tools.translate import _
from datetime import datetime

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


class StockInventory(models.Model):
    _inherit = 'stock.inventory'
    
    code = fields.Char('Code')
    #name_seq = fields.Char(string="Order Ref", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    beginning_balance = fields.Boolean(states={'done': [('readonly', True)]}, help='Mark this indicator if the current setting is the initial load of product stocks.')
    date_done = fields.Datetime('Fecha del ajuste', states={'done': [('readonly', True)]}, help='Fecha referencial para regularizar los movimientos generados por el ajuste de inventario')
    
    def action_validate(self):
        
        if self.beginning_balance:
            #tmpl_obj = self.pool.get('product.template')
            # Obtenemos las líneas del STOCK INVENTORY
            lines = self.env['stock.inventory.line'].search([('inventory_id','=',self.id)])
            for line in lines:
                tmpl_obj = self.env['product.template'].search([('id', '=', line.product_id.product_tmpl_id.id)])
                val ={'standard_price':line.product_unit_cost}
                tmpl_obj.write( val)
        
        if not self.date_done:
            self.date_done = self.date

        result = super(StockInventory, self).action_validate()
        if result:
            data_pool = self.env['ir.model.data']
            try:
                data = data_pool.get_object_reference('kardex', 'stock_inventory_ir_sequence')
                #code = self.env[data[0]].next_by_id(data[1])
                code = self.env[data[0]].get_id(data[1])
            except ValueError:
                raise osv.except_osv(_('Error!'), _('The next sequence value for the inventory failed.'))
            if code:
                self.write({'code': code})
                                   
            
        return result
    
    ##############################################################################################    
    #Métodos para realizar el cálcula de los stock iniciales para cada mes     
    ##############################################################################################

    @api.model
    def automatic_initial_stock_kardex(self):
        self.calculate_initial_stock(datetime.today().year, datetime.today().month, None, None)

    def _add_stock_move_array(self, stock_moves_dict, location, origin_des, product_id, sm):
        if location and stock_moves_dict.get(location.location_id.id):
            
            product_dict = stock_moves_dict.get(location.location_id.id)[1]
            
            if origin_des:
                #Movimiento de salida
                arry_amount = [0.0, sm.product_uom_qty]
            else:
                #Movimiento de entrada
                arry_amount = [sm.product_uom_qty, 0.0]
            
            if product_dict.get(product_id.id):
                arry_amount_main = product_dict.get(product_id.id)
                arry_amount_main[0] += arry_amount[0]
                arry_amount_main[1] += arry_amount[1]
            else:
                product_dict[product_id.id]= arry_amount

    def calculate_initial_stock(self, year, month, warehouses, products):
        stock_moves_dict = {}
        args = []
        arg = ''
        locations = []
        month = int(month)
        
        if products:
            if len(products.ids)==1:
                arg='product_id = '+str(products.id)+' and '
            if len(products.ids)>1:
                arg='product_id in '+str(tuple(products.ids))+' and '
            #args.append(('product_id','in',map(lambda x: x.id, products)))
        
        if not warehouses:
            warehouses = self.env['stock.warehouse'].search([])
        
        location_pool = self.env['stock.location']
        
        for wh in warehouses:
            stock_moves_dict[wh.view_location_id.id] = (wh, {})
            locations += location_pool.search([('location_id', '=', wh.view_location_id.id)])
        
        if locations:
            locations_ids = map(lambda x:x.id, locations)
            #miguel
            ubicaciones=tuple(locations_ids)
            #args.append('|')
            #args.append(('location_id', 'in', locations_ids))
            #args.append(('location_dest_id', 'in', locations_ids))

        #Creamos el filtro por periodo, obtenemos los movimientos del mes anterior
        if month == 1:
            #args.append(('date', '>=', str(year-1)+'-'+str(12)+'-01 05:00:00'))
            date_ini = str(year-1)+'-'+str(12)+'-01 00:00:00'
        else:
            #args.append(('date', '>=', str(year)+'-'+str(month-1)+'-01 05:00:00'))
            date_ini = str(year)+'-'+str(month-1)+'-01 00:00:00'
        
        #args.append(('date', '<', str(year)+'-'+str(month)+'-01 05:00:00'))
        date_fin = str(year)+'-'+str(month)+'-01 00:00:00'
        
        #args.append(('state', 'in', ['done']))     
        
        # Miguel: Cambio para optimizar el código y evitar el uso de sumar o restar horas por la Zona Horaria        
        self._cr.execute("Select id from stock_move where "+arg+"(location_id in %s or location_dest_id in %s) and date at time zone 'utc' at time zone 'pet' >='"+str(date_ini)+"' and date at time zone 'utc' at time zone 'pet' < '"+str(date_fin)+"' and state in ('done')",(ubicaciones,ubicaciones))
        dict_resulset = self._cr.dictfetchall()

        move_ids = []
        for dic in dict_resulset:
            move_ids.append(dic.get('id'))

        #stock_moves = self.env['stock.move'].search(args)
        stock_moves=self.env['stock.move'].search([('id','in',move_ids)])
        
        
        if not stock_moves:
            raise osv.except_osv(_('Error!'), _('No data found'))
        
        #Agrupamos los stock_moves almacén(warehouse) y por producto. 
        for sm in stock_moves:
            product_id = sm.product_id
            self._add_stock_move_array(stock_moves_dict, sm.location_id, True, product_id, sm)
            self._add_stock_move_array(stock_moves_dict, sm.location_dest_id, False, product_id, sm)

        stk_pool = self.env['stock.init.kardex']
        
        for wh_tupl in stock_moves_dict.values():
            for product_id,array_pro in wh_tupl[1].items():
                self.create_write_stock_init_kardex(stk_pool, wh_tupl[0].id, product_id, year, month, array_pro)
        
        #Completamos los registros de stock inicial para los productos restantes, 
        #es decir los productos que no tuvieron movimiento
        
        products = self.env['product.product'].search([])
        for wh in warehouses:
            for product in products:
                self.complete_stock_init_kardex(stk_pool, wh.id, product.id, year, month)
        
    def create_write_stock_init_kardex(self, stk_pool, warehouse_id, product_id, year, month, array_amount):

        if month == 1:
            year_old = year -1
            month_old = 12
        else:
            year_old = year
            month_old = month -1
        
        stk_init_old = stk_pool.search([('warehouse_id','=', warehouse_id),('product_id', '=', product_id),
                                              ('year', '=', year_old),('month', '=', month_old)])
        if not stk_init_old:
            stk_pool.create({'warehouse_id': warehouse_id, 'product_id': product_id, 'year': year_old, 'month': month_old, 
                             'stock_qty': 0.0, 'positive_flow_qty': array_amount[0], 'negative_flow_qty': array_amount[1]})
            amount_init_old = 0.0
        else:
            stk_init_old.write({'positive_flow_qty': array_amount[0], 'negative_flow_qty': array_amount[1]})
            amount_init_old = stk_init_old.stock_qty or 0.0
            
        stk_init = stk_pool.search([('warehouse_id','=', warehouse_id),('product_id', '=', product_id),
                                              ('year', '=', year),('month', '=', month)])
        amount_init_now = amount_init_old + array_amount[0] - array_amount[1]
        
        if not stk_init:
            stk_pool.create({'warehouse_id': warehouse_id, 'product_id': product_id, 'year': year, 'month': month, 
                             'stock_qty': amount_init_now, 'positive_flow_qty': 0.0, 'negative_flow_qty': 0.0})
        else:
            stk_init.write({'stock_qty': amount_init_now})
       
    def complete_stock_init_kardex(self, stk_pool, warehouse_id, product_id, year, month):

        if month == 1:
            year_old = year -1
            month_old = 12
        else:
            year_old = year
            month_old = month -1
        
        stk_init_old = stk_pool.search([('warehouse_id','=', warehouse_id),('product_id', '=', product_id),
                                              ('year', '=', year_old),('month', '=', month_old)])
        if not stk_init_old:
            stk_pool.create({'warehouse_id': warehouse_id, 'product_id': product_id, 'year': year_old, 'month': month_old, 
                             'stock_qty': 0.0, 'positive_flow_qty': 0.0, 'negative_flow_qty': 0.0})
            amount_init_old = 0.0
            flow_pos = 0.0
            flow_neg = 0.0
        else:
            amount_init_old = stk_init_old.stock_qty or 0.0
            flow_pos = stk_init_old.positive_flow_qty or 0.0
            flow_neg = stk_init_old.negative_flow_qty or 0.0
            
        stk_init = stk_pool.search([('warehouse_id','=', warehouse_id),('product_id', '=', product_id),
                                              ('year', '=', year),('month', '=', month)])
        
        if not stk_init:
            stk_pool.create({'warehouse_id': warehouse_id, 'product_id': product_id, 'year': year, 'month': month, 
                             'stock_qty': (amount_init_old + flow_pos - flow_neg), 'positive_flow_qty': 0.0, 'negative_flow_qty': 0.0})
