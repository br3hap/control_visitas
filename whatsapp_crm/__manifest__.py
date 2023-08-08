# -*- coding: utf-8 -*-
{
    'name': "whatsapp_crm",
    'summary': """
        Integra la comunicación con whatsapp para CRM.
    """,
    'description': """
        CREATE MRAMIREZ=>30/09/2020.\n
        Agrega en CRM boton de envio de mensajes a whatsap.\n
        Agrega en ajustes la activacion de whatsapp para CRM.
    """,
    'author': "CONASTEC",
    'website': "https://www.conastec.com.pe/",
    'category': 'whatsapp',
    'version': '0.1',
    'depends': ['crm','whatsapp'],
    'data': [
        'views/crm_lead.xml',
        'views/res_config_settings_views.xml',
    ],
}
