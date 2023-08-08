# -*- coding: utf-8 -*-
{
    'name': 'Debit Note',
    'category': 'Accounting & Finance',
    'summary': 'Module that adds the functionality of electronic debit notes.',
    'author': 'CONASTEC S.R.L.',
    'depends': ['sale', 'sunat_catalogue','fields_for_credit_note','electronic_invoice','account_debit_note'],
    'data': [
        'views/account_move_view.xml',
        'wizards/account_debid_note.xml'
        ],
    'installable': True,
    'auto_install': False,
}
