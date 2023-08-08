# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Cierre de Períodos",
    "summary": """
        Módulo que cierra un periodo para evitar registro o eliminación de
        operaciones para un periodo cerrado.
        """,
    "description": """
        Create: DMisahuaman 30062021
        Se habilita permiso de acceso al menú para Abrir y cerrar períodos
        Se habilita botones en formulario de período contable
        """,
    "category": 'invoice',
    "version": "13.01",
    "author": "CONASTEC",
    "website": "https://www.conastec.com.pe/",
    "installable": True,
    "depends": ["account","account_period"],
    "data": [
        "security/close_open_security.xml",
        "security/ir.model.access.csv",
        "wizards/close_open_period.xml",],
}
