# -*- coding: utf-8 -*-
{
    'name': 'Ajuste contable de Inventario',
    'category': 'inventory',
    'description': '* DNINACO: V1-23/09/2020',
    'summary': """* Modulo que se encarga de modmodificar la categoria del producto
                agregando campos para el seteo de cuentas contables para el ajuste de inventario,
                * Modifica la función que genera los asientos al validar el ajuste.
                """,
    'author': 'CONASTEC',
    'depends': ['stock_account',
        ],
    'data': [
        'view/product_category_view.xml',
        ],
    'installable': True,
    'auto_install': False,
}
