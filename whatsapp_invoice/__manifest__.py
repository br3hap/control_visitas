# -*- coding: utf-8 -*-
{
    'name': "whatsapp_invoice",
    'summary': """
        Integra la comunicación con whatsapp para facturacion.
    """,
    'description': """
        CREATE MRAMIREZ=>30/09/2020.\n
        Agrega en Facturacion boton de envio de mensajes a whatsap.\n
        Agrega en ajustes la activacion de whatsapp para facturacion.
    """,
    'author': "CONASTEC",
    'website': "https://www.conastec.com.pe/",
    'category': 'whatsapp',
    'version': '0.1',
    'depends': ['account','whatsapp'],
    'data': [
        'views/account_move.xml',
        'views/res_config_settings_views.xml',
    ],
}
