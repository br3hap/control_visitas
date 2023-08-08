# -*- coding: utf-8 -*-
{
    'name': 'Multi Product Selection',
    'author': 'CONASTEC',
    'version': '13.0.0.1',
    'depends': ['base', 'sale_management', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale.xml',
        'views/product.xml'
    ],
    
    'sequence': 1,
    'auto_install': False,
    'installable': True,
    'application': False,
    'license': 'OPL-1',

}
