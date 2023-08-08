from odoo import api, fields, models
from odoo.tools.misc import format_date

class ShippingTrace(models.Model):
    _name = 'shipping.trace'
    _description = 'Seguimiento'
    _inherit = ['mail.thread', 'portal.mixin']
    
    name = fields.Char(string='Tracking Reference',readonly=True)
        
    order_ref = fields.Char(string='Referencia de Orden', track_visibility='onchange',readonly=True)
    
    picking_id = fields.Many2one(comodel_name='stock.picking', string='Picking', track_visibility='onchange',readonly=True)
    
    picking_date = fields.Datetime(string='Picking Date', track_visibility='onchange',readonly=True)
    
    scheduled_shipping_date = fields.Date(string='Fecha programada de de envio', track_visibility='onchange',readonly=True)
    
    partner_id = fields.Many2one(comodel_name='res.partner', string='Cliente',readonly=True)
    
    
    shipping_status_id = fields.Many2one(comodel_name='shipping.status', string='Estado de Despacho', track_visibility='onchange')
    
    
    
    shipping_company_id = fields.Many2one(comodel_name='res.partner', string='Shipping Company', domain=[('is_delivery_company','=',True)],readonly=True)
    
    shipping_carrier_id = fields.Many2one(comodel_name='res.partner', string='Carrier',readonly=True)
    
    vehicle_id = fields.Many2one(comodel_name='shipping.vehicle', string='Vehicle',readonly=True)
    
    vat_name  = fields.Char(string='Identificación', related='shipping_carrier_id.vat',readonly=True)
    
    vehicle_brand = fields.Char(string='Vehicle Branch', related='vehicle_id.brand',readonly=True)
    
    street = fields.Char(string='Direccion', related='picking_id.partner_id.street')
    
    city = fields.Char(string='Ciudad', related='picking_id.partner_id.city_id.name')
    
    
    district = fields.Char(string='Distrito', related='picking_id.partner_id.l10n_pe_district.name')
    
    remark = fields.Text(string='Observaciones')
    
    date_deadline_formatted = fields.Char(compute='_compute_date_deadline_formatted')
    
    shipping_trace_line_ids = fields.One2many(comodel_name='shipping.trace.line', inverse_name='shipping_trace_id', string='Detalle')
    
    color = fields.Integer(string='Color',default=1)
    
    active = fields.Boolean(string='Activo?',default=True)
    
    
    @api.model
    def create(self, vals):
        """
            Create a new record for a model ShippingTrace
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        if vals.get('name','TRCK-000') == 'TRCK-000':
                vals['name'] = self.env['ir.sequence'].next_by_code('delivery.trace.registration') or 'TRCK-000'
        result = super(ShippingTrace, self).create(vals)
        # msg = "Seguimiento " + self.env.ref('delivery_status_trace.shipping_status_1',False).name
        # result.message_post(subject ="1", body=msg, message_type="comment", subtype="mail.mt_comment")
        return result
    
    @api.depends('scheduled_shipping_date')
    def _compute_date_deadline_formatted(self):
        for task in self:
            task.date_deadline_formatted = format_date(self.env, task.scheduled_shipping_date) if task.scheduled_shipping_date else None
            
    def picking_button(self):
        self.ensure_one()
        action = {
            'name': 'Picking',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'target' : 'current',
        }
        picking_ids = self.env['stock.picking'].search([('id','=',self.picking_id.id)])
        if len(picking_ids) == 1:
            picking = picking_ids[0].id
            action['res_id'] = picking
            action['view_mode'] = 'form'
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', picking_ids.ids)]
        return action
        
  
    
    def write(self, values):
        result = super(ShippingTrace, self).write(values)
        if values.get('shipping_status_id'):
            status_name = self.env['shipping.status'].search([('id','=',values.get('shipping_status_id'))])
            msg = status_name.name
            self.message_post(subject ="track", body=msg, message_type="comment", subtype="mail.mt_comment")
        return result
    
    # @api.onchange('shipping_status_id')
    # def on_change_status(self):
    #     msg = self.shipping_status_id.name
    #     return self.message_post(subject ="1", body=msg, message_type="comment", subtype="mail.mt_comment")
    
    
    
    class ShippingTraceLine(models.Model):
        _name = 'shipping.trace.line'
        _description = 'Linea de Despacho'
        _rec_name = 'product_id'
    
        shipping_trace_id = fields.Many2one(comodel_name='shipping.trace', string='Despacho')
        
        product_id = fields.Many2one(comodel_name='product.product', string='Producto')
        
        product_qty = fields.Float(
        'Cantidad',
        digits=0, store=True, help='Quantity in the default UoM of the product')
        product_uom_qty = fields.Float(
        'Demanda Inicial',
        digits='Product Unit of Measure',
        default=0.0, required=True, )
        product_uom = fields.Many2one('uom.uom', 'Unidad de medida', required=True, domain="[('category_id', '=', product_uom_category_id)]")
        product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
        
        partner_id = fields.Many2one(comodel_name='res.partner', string='Cliente')
        
        street = fields.Char(string='Direccion', related='shipping_trace_id.picking_id.partner_id.street', store=False)
    
        city = fields.Char(string='Ciudad', related='shipping_trace_id.picking_id.partner_id.city_id.name', store=False)
        
        
        district = fields.Char(string='Distrito', related='shipping_trace_id.picking_id.partner_id.l10n_pe_district.name', store=False)
        
        remark = fields.Text(string='Observaciones' , related= 'shipping_trace_id.remark', store=False)
        
        
    
    
    
    
