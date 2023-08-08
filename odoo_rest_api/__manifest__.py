# -*- coding: utf-8 -*-
{
    'name': 'Odoo rest Api',
    'version': '13.0.1',
    'description': 'Odoo rest Api',
    'summary': 'Odoo rest Api',
    'author': 'Conastec',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'base',
        'account',
        'contacts',
        'product',
        'web'
    ],
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'views/odoo_rest_api_view.xml',
        'views/customer_rest_api_view.xml',
        'views/account_move_rest_api_view.xml',
        'views/account_journal.xml',
        'views/product_pricelist.xml'

    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}