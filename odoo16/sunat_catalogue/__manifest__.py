# -*- coding: utf-8 -*-
{
    'name': "Sunat Catalogue",

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
    'depends': ['base', 'account'],

    # always loaded
    'data': [

        'views/catologue_menu.xml',
        'security/ir.model.access.csv',
        'data/peb.catalogue.01.csv',
        'data/peb.catalogue.05.csv',
        'data/peb.catalogue.09.csv',
        'data/peb.catalogue.10.csv',
        'data/peb.catalogue.12.csv',
        'data/peb.catalogue.51.csv',
        'data/peb.catalogue.07.csv',
        'data/peb.catalogue.20.csv',
        'data/peb.catalogue.18.csv',
        'data/peb.catalogue.21.csv',
        'data/peb.shipping.status.sunat.csv',

        'views/peb_catalogue_01.xml',
        'views/peb_catalogue_05.xml',
        'views/peb_catalogue_09.xml',
        'views/peb_catalogue_10.xml',
        'views/peb_catalogue_12.xml',
        'views/peb_catalogue_07.xml',
        'views/peb_catalogue_51.xml',
        'views/peb_catalogue_20.xml',
        'views/peb_catalogue_18.xml',
        'views/peb_catalogue_21.xml',
        'views/peb_shipping_status_sunat.xml',
    ],
}

