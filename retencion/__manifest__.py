# -*- coding: utf-8 -*-
{
    'name': "Retencion",

    'summary': """
        Modulo que agrega la funcionalidad de retenciones en odoo
        """,

    'description': """
       Modulo que agrega la funcionalidad de retenciones en odoo
    """,

    'author': "CONASTEC",

    'category': 'invoice',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'fields_for_sunat', 'stock_account',  'product'],

    # always loaded
    'data': [
        'views/account_move.xml',
    ],
}
