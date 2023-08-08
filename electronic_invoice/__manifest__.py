# -*- coding: utf-8 -*-
{
    'name': "Electronic Invoice",

    'summary': """
        Module that adds the fields and shipping for electronic invoicing
        """,

    'description': """
       * DNINACO 05/08/2020
        - Se agrego para que al momento de aceptar ebis el comprobante
            tambien se obtenfa el pdf de EBIS
    """,

    'author': "CONASTEC",

    'category': 'invoice',
    'version': '16.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','sunat_catalogue', 
                'fields_for_sunat', 'fields_for_credit_note',
                'detraction', 'export_sale', 'anticipos','journal_sequence', 'stock'],

    # always loaded
    'data': [
        'views/account_journal.xml',
        'views/res_company.xml',
        'views/account_move.xml',
        'views/mensaje_emergente_view.xml',
        'views/recibir_comprobante_pago_respuesta_view.xml',
        'views/logs_comprobante_view.xml',
        'security/ir.model.access.csv',
        'views/baja_comprobante.xml',
        'views/sale_order_view.xml',
        'views/stock_picking_view.xml',
        'views/cuotas.xml',
    ],
}
