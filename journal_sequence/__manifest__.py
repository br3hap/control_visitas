# -*- coding: utf-8 -*-

{
    'name': 'Journal Sequence',
    'version': '16.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Odoo Journal Sequence, Journal Sequence For Invoice',
    'description': 'Odoo Journal Sequence, Journal Sequence For Invoice',
    'sequence': '1',
    'author': 'Conastec',
    'depends': ['account'],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/account_journal.xml',
        'views/account_move.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': "create_journal_sequences",
}
