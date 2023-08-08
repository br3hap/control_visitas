# -*- coding: utf-8 -*-
{
    'name': "delivery_status_trace",

    'summary': """
       MODULO PARA HACER SEGUIMIENTO A LOS DESPACHOS DE LOS PEDIDOS""",

    'description': """
        Este modulo implementa la funcionalidad de seguimiento en el despacho de los pedidos
    """,

    'author': "Felipe Guerrero",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','delivery','stock'],

    # always loaded
    'data': [
        'report/delivery_status_trace_report.xml',
        'report/delivery_trace_action_report.xml',
        
        'data/shipping_status.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        
        'views/shipping_status_views.xml',
        'views/shipping_trace_views.xml',
        'views/stock_picking_views.xml',
        'views/settings_inherit_views.xml',
        'views/res_partner_views.xml',
        'views/shipping_vehicle_views.xml',
        'views/shipping_trace_line_views.xml',
    ],
    # only loaded in demonstration mode
 
    'application' : True,
    'uninstall_hook': '_uninstall_hook',
}
