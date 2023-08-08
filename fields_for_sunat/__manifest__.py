# -*- coding: utf-8 -*-
{
    'name': "Fields for Sunat",

    'summary': """
        Field containing the fields required by sunat
        """,

    'description': """
        Field containing the fields required by sunat
    """,

    'author': "CONASTEC",

    'category': 'invoice',
    'version': '16.0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base','uom','stock','sunat_catalogue','l10n_pe'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/uom_uom.xml',
        'views/stock_warehouse.xml',
        'views/account_move.xml',
        'views/account_tax.xml',
        'views/product_template_view.xml',
    ],
}
