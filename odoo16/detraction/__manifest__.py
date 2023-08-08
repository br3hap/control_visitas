# -*- coding: utf-8 -*-
{
    'name': "Detraction",

    'summary': """
        module that stores sunat's catalogs""",

    'description': """
       module that stores sunat's catalogs
    """,

    'author': "CONASTEC",

    'category': 'invoice',
    'version': '16.0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'fields_for_sunat', 'stock_account',  'product'],

    # always loaded
    'data': [

        'views/menu_detraction.xml',
        'security/ir.model.access.csv',

        'data/peb.catalogue.paid.detraction.csv',
        'data/peb.catalogue.service.spot.csv',
        'data/peb.catalogue.type.operation.detraction.csv',

        'views/peb_catalogue_paid_detraction.xml',
        'views/peb_catalogue_service_spot.xml',
        'views/peb_catalogue_type_operation_detraction.xml',
        'views/account_move.xml',

        'views/product_category.xml',
        'views/product_template.xml',
    ],
}
