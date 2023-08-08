# -*- coding: utf-8 -*-
{
    'name': "whatsapp_sale",
    'summary': """
        Envio de las cotizaciones a whatsapp.
    """,
    'description': """
        CREATE MRAMIREZ=>30/09/2020.\n
        Agrega en cotizaciones el boton de envio de mensajes a whatsap.\n
        Agrega en ajustes la activacion de whatsapp para cotizaciones.
    """,
    'author': "CONASTEC",
    'website': "https://www.conastec.com.pe/",
    'category': 'whatsapp',
    'version': '0.1',
    'depends': ['sale','whatsapp'],
    'data': [
        'views/sale_order.xml',
        'views/res_config_settings_views.xml',
    ],
}
