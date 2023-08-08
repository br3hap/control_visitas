# -*- coding: utf-8 -*-
{
    'name': "Guia de Remisión",

    'summary': """
        Modulo que permite generar la guía de remisión electrónica.
        """,

    'description': """
       Modulo que permite generar la guía de remisión electrónica.
    """,

    'author': "CONASTEC S.R.L.",

    'category': 'stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock','account','sunat_catalogue', 
                'fields_for_sunat','electronic_invoice','l10n_latam_invoice_document',
                'delivery_status_trace', 'total_peso_picking'],

    # always loaded
    'data': [
        'views/stock_picking_view.xml',
        'views/ir_sequence_view.xml',
        'views/res_company_view.xml',
        'views/recibir_comprobante_pago_respuesta_view.xml',
        'views/logs_guia_remision_view.xml',
        'security/ir.model.access.csv',
    ],
}
