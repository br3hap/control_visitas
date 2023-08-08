# -*- coding: utf-8 -*-
{
    'name': "Facturación por Anticipo",

    'summary': """
        Facturación por anticipo
        """,

    'description': """
       Agrega la modificación para emitir por anticipo y la deducción de anticipo
    """,

    'author': "CONASTEC",

    'category': 'invoice',
    'version': '16.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move.xml',
    ],
}
