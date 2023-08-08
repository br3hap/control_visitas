from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    shipping_trace_count = fields.Integer(string='Shipping' , compute='_get_shipping_trace_count')
    
    shipping_company_id = fields.Many2one(comodel_name='res.partner', string='Shipping Company', domain=[('is_delivery_company','=',True)])
    
    shipping_carrier_id = fields.Many2one(comodel_name='res.partner', string='Carrier')
    
    vehicle_id = fields.Many2one(comodel_name='shipping.vehicle', string='Vehicle')
    
    vat_name  = fields.Char(string='Nro Identificacion', related='shipping_carrier_id.vat')
    
    vehicle_brand = fields.Char(string='Vehicle Branch', related='vehicle_id.brand')
    
    
    b_shipping_trace = fields.Boolean(string='Flag Shipping' , default=False)
    
    scheduled_shipping_date = fields.Date(string='Fecha Programada de transporte')
    
    b_allow_tracking = fields.Boolean(string='Allow Tracking?',default=False)
    
    remark = fields.Text(string='Observaciones')
    
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier", check_company=True)
    
    @api.onchange('shipping_company_id')
    def _shopping_carrier_domain(self):
        return {'domain' : {'shipping_carrier_id' : [('delivery_company_id','=',self.shipping_company_id.id)]}}
    
    @api.onchange('shipping_carrier_id')
    def _shopping_vehicle_domain(self):
        return {'domain' : {'vehicle_id' : [('partner_id','=',self.shipping_company_id.id)]}}
    
    
    def _get_shipping_trace_count(self):
        for stock in self:
            shipping_ids = self.env['shipping.trace'].search([('picking_id','=',stock.id)])
            stock.shipping_trace_count = len(shipping_ids)

    def shipping_trace_button(self):
        self.ensure_one()
        action = {
            'name': 'Despachos',
            'type': 'ir.actions.act_window',
            'res_model': 'shipping.trace',
            'target' : 'current,'
        }
        shipping_trace_ids = self.env['shipping.trace'].search([('picking_id','=',self.id)])
        if len(shipping_trace_ids) == 1:
            shipping_trace = shipping_trace_ids[0].id
            action['res_id'] = shipping_trace
            action['view_mode'] = 'form'
            form_view = [(self.env.ref('delivery_status_trace.shipping_trace_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', shipping_trace_ids.ids)]
        return action
    

    def generate_shipping_trace(self):
        lines_ids = []
        
        for item in self.move_ids_without_package:
            lines_ids.append((0,0, {
                'product_id' : item.product_id.id,
                'product_qty' : item.product_qty,
                'product_uom_qty' : item.product_uom_qty,
                'product_uom' :  item.product_uom.id,
                'product_uom_category_id': item.product_uom_category_id.id,
                'partner_id' : item.partner_id.id,
            }))
        
        
        vals = {
                'order_ref' : self.origin,
                'picking_id' : self.id,
                'picking_date' : self.date,
                'partner_id': self.partner_id.id,
                'scheduled_shipping_date' : self.scheduled_shipping_date,
                'shipping_status_id' : self.env['shipping.status'].search([('sequence','=',1)],limit=1).id,
                'shipping_company_id' : self.shipping_company_id.id,
                'shipping_carrier_id' : self.shipping_carrier_id.id,
                'vehicle_id' : self.vehicle_id.id,
                'shipping_trace_line_ids' : lines_ids,
                'remark' : self.remark,
                'active' : True
        }
       
        
        if self.carrier_tracking_ref:
            shipping_ids = self.env['shipping.trace'].search([('name','=',self.carrier_tracking_ref)])
            cancel = self.env.ref('delivery_status_trace.shipping_status_7',False).id
            for ship in shipping_ids:
                ship.shipping_status_id = cancel
                
        obj_shipping_trace = self.env['shipping.trace'].sudo().create(vals)
        self.carrier_tracking_ref = obj_shipping_trace.name 
                   
        return {
            'effect': {
                        'fadeout': 'slow',
                        'message':  _('Seguimiento %s Registrado' % self.carrier_tracking_ref ),
                        'type': 'rainbow_man',
            }
        } 
   
    
    @api.model
    def default_get(self,fields):
        res = super(StockPicking, self).default_get(fields)
        allow_shipping_trace = bool(self.env['ir.config_parameter'].sudo().get_param('delivery_status_trace.allow_shipping_trace'))
        res['b_allow_tracking'] = allow_shipping_trace
        return res
    
    @api.constrains('carrier_tracking_ref')
    def _check_tracking_ref(self):
        if self.carrier_tracking_ref != '' or self.carrier_tracking_ref != False:
            tracking_ref_ids = self.env['shipping.trace'].search([('name','=',self.carrier_tracking_ref)])
            if len(tracking_ref_ids)>=2:
                raise ValidationError('El numero de referencia %s ya existe' % (self.carrier_tracking_ref))
            
            
            
class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'
        
             
    def _create_returns(self):
        for rec in self:
            if rec.picking_id.carrier_tracking_ref != False:
                track = self.env['shipping.trace'].search([('name','=',rec.picking_id.carrier_tracking_ref)],limit=1)
                if track.shipping_status_id.id != self.env.ref('delivery_status_trace.shipping_status_7',False).id:
                    raise ValidationError("Primero tiene que cancelar la orden de seguimiento %s asociada al picking" % rec.picking_id.carrier_tracking_ref)
        values = super(ReturnPicking, self)._create_returns()
        return values