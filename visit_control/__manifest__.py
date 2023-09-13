# -*- coding: utf-8 -*-
{
    'name': "Visit Control",

    'summary': """
        Module to keep track of visits made to patients in a hospital.
        """,

    'description': """
       Module to keep track of visits made to patients in a hospital.
    """,

    'author': "Breithner Aquituari",

    'category': '',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'hr_expense'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/visit_control.xml',
        'data/sequence.xml'
    ],
}
