# -*- coding: utf-8 -*-
{
    'name': "Partner Custom",

    'summary': """Pattern Custom""",

    'description': """
        Pattern Custom
        CREATE:
        *21072020 => MRamirez
        UPDATES:
    """,

    'author': "CONASTEC",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Res Pattern',

    # any module necessary for this one to work correctly
    'depends': ['base','l10n_pe','base_setup','l10n_latam_base','base_address_extended'],

    # always loaded
    'data': [
        'views/partner_view.xml',
    ],
}
