#######################################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
#######################################################################################

from odoo import api, fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def _get_type_credit_note(self):
        return self.env.ref("l10n_pe_edi_catalog.l10n_pe_edi_cat09_01").id

    l10n_pe_edi_reversal_type_id = fields.Many2one(
        comodel_name="l10n_pe_edi.catalog.09",
        string="Credit note type",
        default=_get_type_credit_note,
        help="Catalog 09: Types of Credit note",
    )

    @api.depends("move_ids")
    def _compute_available_journal_ids(self):
        res = super(AccountMoveReversal, self)._compute_available_journal_ids()
        for rec in self:
            move_ids = self.env["account.move"].browse(rec.move_ids.ids)
            if all(move.l10n_pe_edi_is_einvoice for move in move_ids):
                rec.available_journal_ids = self.env["account.journal"].search(
                    [("l10n_latam_document_type_id.code", "=", "07")]
                )
        return res

    @api.depends("move_ids", "available_journal_ids")
    def _compute_journal_id(self):
        res = super(AccountMoveReversal, self)._compute_journal_id()
        for rec in self:
            move_ids = self.env["account.move"].browse(rec.move_ids.ids)
            if all(move.l10n_pe_edi_is_einvoice for move in move_ids):
                rec.journal_id = (
                    rec.available_journal_ids
                    and rec.available_journal_ids[0]._origin
                    or False
                )
        return res

    @api.depends("journal_id")
    def _compute_document_type(self):
        for rec in self:
            rec.l10n_latam_document_type_id = rec.journal_id.l10n_latam_document_type_id

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        res.update(
            {
                "l10n_pe_edi_reversal_type_id": self.l10n_pe_edi_reversal_type_id.id,
            }
        )
        return res
