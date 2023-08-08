# -*- coding: utf-8 -*-
{
    'name': "Invoice Expense",

    'summary': """
        Modulo que modifica la funcionalidad de l modulo de gastos.
        """,

    'description': """
       Modulo que modifica la funcionalidad de l modulo de gastos.
    """,

    'author': "CONASTEC",

    'category': 'expense',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_expense', 'account', 'journal_account_receivable', 'base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_expense_views.xml',
    ],
}
