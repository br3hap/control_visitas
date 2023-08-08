# -*- coding: utf-8 -*-
{
    'name': "Fields for Credit Note",

    'summary': """
       Module that adds fields related to the credit note""",

    'description': """
      * DNINACO 05/08/2020
        - SE AGREGO LAS TRADUCCIONES
        - SE AGREGO VALIDACIONES SEGUN EL TIPO DE DOCUMENTO PARA LA REFERENCIA
    """,

    'author': "CONASTEC",

    'category': 'invoice',
    'version': '16.0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sunat_catalogue'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move.xml',
        'views/account_move_reversal.xml'
    ],
}
