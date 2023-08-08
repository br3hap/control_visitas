# -*- coding: utf-8 -*-
{
    'name': 'Kardex Interface',
    'category': 'Warehouse Management',
    'summary': 'Module for the generation of the kardex file according to the Sunat format.',
    'author': 'CONASTEC S.R.L.',
    'depends': ['stock','sunat_catalogue'],
    'data':[
        'wizards/kardex_filter_wizard.xml',
        'wizards/menu_item_kardex.xml',
        'views/uom_uom_view.xml',
        'views/stock_view.xml',
        'views/product_template_view.xml',
        'views/stock_inventory_view.xml',
        'data/cron_kardex_initial_stocks.xml',
        'data/stock_inventory_sequence.xml',
        #'data/stock_inventory_seq.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}