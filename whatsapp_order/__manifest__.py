# -*- coding: utf-8 -*-
{
    'name': "whatsapp_order",

    'summary': """
        Integra la comunicación con whatsapp para pedidos.
    """,
    'description': """
        CREATE MRAMIREZ=>30/09/2020.\n
        Agrega en pedidos el boton de envio de mensajes a whatsap.\n
        Agrega en ajustes la activacion de whatsapp para pedidos.
    """,
    'author': "CONASTEC",
    'website': "https://www.conastec.com.pe/",
    'category': 'whatsapp',
    'version': '0.1',
    'depends': ['whatsapp','point_of_sale'],
    'data': [
        'views/pos_order.xml',
        'views/res_config_settings_views.xml',
    ],
}
