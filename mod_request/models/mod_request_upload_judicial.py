# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class mod_request_upload_judicial_purchased(models.Model):
    _name = 'mod.request.upload.judicial.purchased'
    _description = _("upload attachments purchased")

    mod_request_id = fields.Many2one('mod.request', string='Cod. Request')
    file_purchased = fields.Binary(string='File Purchased')
    file_name_purchased = fields.Char(string='File Name Purchased')
    date = fields.Datetime(string='Date',copy = False, default = lambda self: fields.datetime.now())
    state = fields.Boolean(string="Send", default=False)


class mod_request_upload_judicial_supported(models.Model):
    _name = 'mod.request.upload.judicial.supported'
    _description = _("upload attachments supported")

    mod_request_id = fields.Many2one('mod.request', string='Cod. Request')
    file_supported = fields.Binary(string='File Supported')
    file_name_supported = fields.Char(string='File Name Supported')
    date = fields.Datetime(string='Date',copy = False, default = lambda self: fields.datetime.now())


