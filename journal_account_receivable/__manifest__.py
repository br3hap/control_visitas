# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Journal Account Receivable',
    'version': '1.0',
    'category': 'Sales/Sales',
    'summary': 'Journal Account Receivable',
    'description': """
        Módulo que agrega cuenta contable de pago/cobro en los diarios. 
        La cuenta que se configure en el diario será la utilizada por defecto en los asientos generados.
    """,
    'depends': ['account'],
    'data': [
        'views/account_journal_view.xml',
        
    ],
    
    'qweb': [
    ],
    'installable': True,
    'auto_install': False
}