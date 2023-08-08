# -*- coding: utf-8 -*-
{
    'name': "Export for Sale",

    'summary': """
        this module allows emission by export""",

    'description': """
       this module allows emission by export
    """,

    'author': "CONASTEC",

    'category': 'invoice',
    'version': '16.0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move.xml',
    ],
}
