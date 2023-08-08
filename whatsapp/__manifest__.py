# -*- coding: utf-8 -*-
{
    'name': "whatsapp",
    'summary': """
        Integra la comunicación con whatsapp.
    """,
    'description': """
        CREATE MRAMIREZ=>28/09/2020.\n
        Agrega en contactos boton de envio de mensajes a whatsap.\n
        Agrega en ajustes la activacion de whatsapp y el ingreso de la url.
    """,
    'author': "CONASTEC",
    'website': "https://www.conastec.com.pe/",
    'category': 'whatsapp',
    'version': '0.1',
    'depends': ['base','base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/whatsapp_send_message.xml',
        'views/res_config_settings_views.xml',
    ],
}
