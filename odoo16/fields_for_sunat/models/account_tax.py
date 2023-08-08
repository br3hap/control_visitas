# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_tax(models.Model):
    _inherit = 'account.tax'

    igv_affectation = fields.Many2one('peb.catalogue.07', 'IGV Affectation')
    tax_internactional_code = fields.Char('Tax Internacional Code')

    l10n_pe_edi_tax_code = fields.Selection(selection_add=[
        ('1000', 'IGV - General Sales Tax'),
        ('1016', 'IVAP - Tax on Sale Paddy Rice'),
        ('2000', 'ISC - Selective Excise Tax'),
        ('9995', 'EXP - Exportation'),
        ('9996', 'GRA - Free'),
        ('9997', 'EXO - Exonerated'),
        ('9998', 'INA - Unaffected'),
        ('7152', 'Impuesto a la bolsa'),
        ('9999', 'OTROS - Other taxes')
    ], string='EDI peruvian code')

class AccountTaxTemplate(models.Model):
    _inherit = "account.tax.template"
    l10n_pe_edi_tax_code = fields.Selection(selection_add=[
        ('1000', 'IGV - General Sales Tax'),
        ('1016', 'IVAP - Tax on Sale Paddy Rice'),
        ('2000', 'ISC - Selective Excise Tax'),
        ('9995', 'EXP - Exportation'),
        ('9996', 'GRA - Free'),
        ('9997', 'EXO - Exonerated'),
        ('9998', 'INA - Unaffected'),
        ('7152', 'Impuesto a la bolsa'),
        ('9999', 'OTROS - Other taxes')
    ], string='EDI peruvian code')

    def _get_tax_vals(self, company, tax_template_to_tax):
        val = super()._get_tax_vals(company, tax_template_to_tax)
        val.update({
            'l10n_pe_edi_tax_code': self.l10n_pe_edi_tax_code,
            'l10n_pe_edi_unece_category': self.l10n_pe_edi_unece_category,
        })
        return val
