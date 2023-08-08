# -*- coding: utf-8 -*-


from . import controllers
from . import models
from . import report

from odoo import api, fields, SUPERUSER_ID, _

def _uninstall_hook(cr, registry):
    cr.execute(
        "DELETE FROM ir_config_parameter WHERE key in ('delivery_status_trace.allow_shipping_trace','delivery_status_trace.allow_shipping_trace')"
        )