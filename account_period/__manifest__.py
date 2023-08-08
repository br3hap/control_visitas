# -*- coding: utf-8 -*-
{
    'name': "Período Contable",

    'summary': """
        Módulo que contiene el mantenimiento de períodos contables.
        """,

    'description': """
        Módulo que contiene el mantenimiento de períodos contables.
    """,

    'author': "",
    'website': "",

    'category': 'invoice',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [

        'views/account_period_menu.xml',
        'security/ir.model.access.csv',
        'views/account_period.xml',
        'views/account_move.xml',
    ],
}
