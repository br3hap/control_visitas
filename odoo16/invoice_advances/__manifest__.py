{
    'name': 'Invoice Advance',
    'version': '13.0.1',
    'description': 'Invoice Advance',
    'summary': 'Invoice Advance',
    'author': 'conastec',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'sale_management',
        'anticipos'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'views/sale_order.xml',
    ],
    'auto_install': False,
    'application': False,
}