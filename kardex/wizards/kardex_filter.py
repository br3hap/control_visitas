# -*- coding: utf-8 -*-
from odoo import models, fields, api
#from datetime import datetime
from datetime import datetime, timedelta
import time
time.time()


class KardexFilter(models.TransientModel):
    _name= 'kardex.filter'
    
    def _get_month():
        return str(datetime.today().month)
    
    def _get_year():
        return datetime.today().year
    
    month = fields.Selection([('1','Enero'),
                             ('2','Febrero'),
                             ('3','Marzo'),
                             ('4','Abril'),
                             ('5','Mayo'),
                             ('6','Junio'),
                             ('7','Julio'),
                             ('8','Agosto'),
                             ('9','Septiembre'),
                             ('10','Octubre'),
                             ('11','Noviembre'),
                             ('12','Diciembre')],"Month", default= _get_month(), required=True)
    year = fields.Integer(required=True, string="Year", digits=(4), default=_get_year())
    #warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouses')
    warehouse_ids = fields.Many2one('stock.warehouse', string='Warehouses', required=True)
    product_ids = fields.Many2many('product.product', string='Products')
    include_null_products = fields.Boolean(string='Incluir saldos nulos', help='Si activa esta opción se incluirán en el reporte productos son stock igual a cero y negativos.')
    
    #@api.multi
    def export_excel(self):
        report_kardex = self.env['report.kardex'].generate_excel(self.year, self.month, self.warehouse_ids, self.product_ids, self.include_null_products)
        return {
            'view_mode': 'form',
            'res_id': report_kardex.id,
            'res_model': 'report.kardex',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
            }

    def datetimeformat(self, strdate):
        return datetime.strptime(strdate, "%Y-%m-%d %H:%M:%S")

    
    #@api.multi
    def _write_standard_price (self, product_id, stand_price):
        tmpl_obj = self.pool.get('product.template')
        val ={'standard_price':stand_price}
        tmpl_obj.write(self._cr, self._uid, [product_id.product_tmpl_id.id], val, context=self._context)
    
    #@api.multi
    def fix_reverse_move(self):
        #try:
        self._cr.execute("SELECT id,date from stock_move \
                            where  origin_returned_move_id>0 \
                            and state='done' \
                            and date between '2019-01-01 00:00:00' and '2019-04-30 23:59:59' \
                            order by date")
        res = self._cr.dictfetchall()
        for dict in res:
            id = dict['id']
            date_string = dict['date']
            date = time.mktime(datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S').timetuple())
            #self._cr.execute("UPDATE stock_move sm SET date='"+str(date_string)+"'+ (1 ||' minutes')::interval FROM stock_move WHERE sm.id ="+str(id))
            self._cr.execute("UPDATE stock_move sm SET date=((select date from stock_move where id="+str(id)+")+ (1 ||' minutes')::interval) FROM stock_move WHERE sm.id ="+str(id))
        #except:
        #    pass
        return True    
     
    #@api.multi
    def calculate_initial_stock(self):
        self.env['stock.inventory'].calculate_initial_stock(self.year, self.month, self.warehouse_ids, self.product_ids)
        return
  
    
    
