# -*- coding: utf-8 -*-
{
    'name': "Rellenado de Cuotas",

    'summary': """
        Modulo que permite rellenar las  cuotas de forma automatica
        """,

    'description': """
       Modulo que permite rellenar lascuotas deforma automatica
    """,

    'author': "CONASTEC",

    'category': 'invoice',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['electronic_invoice'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_move.xml',
    ],
}
