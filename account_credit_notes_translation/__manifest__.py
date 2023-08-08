# -*- coding: utf-8 -*-
{
    'name': "Account credit note translation",

    'summary': """
        Se Cambia en menú de Facturas rectificativas a Notas de crédito
        Para clientes y proveedores""",
    
    'description': """
        fecha de creacion: 03/02/21
        Actualización 27072021
        Se agrega filtros para Facturas y Notas de crédito de proveedores.
        """,

    'author': "CONASTEC",
    'website': "https://www.conastec.com.pe/",

    'category': 'invoice',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','fields_for_credit_note','l10n_latam_invoice_document'],

    # always loaded
    'data': [
        'views/credit_notes.xml',
    ],
}
