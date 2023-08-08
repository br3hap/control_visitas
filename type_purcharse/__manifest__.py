# -*- coding: utf-8 -*-
{
    'name': "type_purcharse",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Este módulo se creó para diferenciar las compras hechas a nivel nacional o internacional
    """,

    'author': "Conastec", 
 
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','account','account_credit_notes_translation'],

    # always loaded
    'data': [ 
        'views/views.xml', 
        'views/search.xml', 
    ], 
}