# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import except_orm

class account_move(models.Model):
    _inherit = "account.move"

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            journal = self.journal_id

            value_dic = dict(currency_id=journal.currency_id.id or journal.company_id.currency_id.id,
                             company_id=journal.company_id.id)
            """
            if journal.cuenta_cobrar_id.id:
                value_dic.update(account_id=journal.cuenta_cobrar_id.id)
            """
            if journal.sunat_document_type.code == u'08':
                # self.is_note_document = True
                value_dic.update(is_note_document=True)
            else:
                value_dic.update(is_note_document=False)

            # if value_dic.get('is_note_document') and self.move_type in ('out_invoice','out_refund'):
            #     return dict(value=value_dic, domain={
            #         'reason': [('type', '=', '4')]})  # domain=dict(invoice_refund_type=[('tipo','=',4)])
            # else:
            #     return dict(value=value_dic, domain={
            #         'reason': [('type', '!=', '4')]})
            if value_dic.get('is_note_document') and self.move_type in ('out_invoice','out_refund'):
                return dict(value=value_dic)  # domain=dict(invoice_refund_type=[('tipo','=',4)])
            else:
                return dict(value=value_dic)    

        return {}

    def validate_credit_note(self, invoice_id):
        message, invoice_id = self.validate_invoice_id_note(invoice_id)
        if message:
            raise except_orm(_('Related voucher'), message)
        return invoice_id

    def validate_invoice_id_note(self, invoice_id):
        message = ''
        series_correlative = ''
        if invoice_id:
            invoice_id = invoice_id.upper().strip()
            series_correlative = invoice_id.split('-')
            if self.journal_id and self.journal_id.sequence_id.prefix and self.journal_id.sequence_id.prefix[:1] != invoice_id[:1]:
                message = _("El tipo de Documento relacionado no se corresponde con el Diario seleccionado")

        if len(series_correlative) != 2 or len(series_correlative[0]) != 4 or len(series_correlative[1]) != 8:
            message = _("the structure of the value of 'Related voucher' is invalid."
                        "The series must be of 4 characters and the correlative of 8 digits, these two values ​​separated by hyphen."
                        "In case of a physical voucher complete the series with a zero forward.")

        if not message:
            try:
                int(series_correlative[1])
            except:
                message = _("The correlative of the 'related receipt' must be only numbers.")

        return (message, invoice_id)

    @api.onchange('related_document')
    def onchange_invoice_id(self):
        invoice_id = self.related_document
        is_note_document = self.is_note_document
        journal_id = self.journal_id

        result_dict = {}
        if invoice_id:

            invoice_id = self.validate_credit_note(invoice_id)
            #result_dict.update(invoice_id=invoice_id)
            result_dict.update(related_document=invoice_id)
            invoice = self.env['account.move'].search([('name', '=', invoice_id)])
            currency_id = False

            if not invoice:
                invoice_prefix = invoice_id[:1]
            else:
                result_dict.update(partner_id=invoice.partner_id.id)
                result_dict.update(date_related_document=invoice.invoice_date)
                if invoice.journal_id.sequence_id:
                    invoice_prefix = invoice.journal_id.sequence_id.prefix[:1]
                    currency_id = invoice.journal_id.currency_id or 'CURRENCY_COMPANY'
                elif invoice.number:
                    invoice_prefix = invoice.number[:1]

            if invoice_prefix in ('F', 'B'):
                journal_selected = False
                journal_current = self.env['account.journal'].browse(journal_id.id)

                if (journal_current.sequence_id and journal_current.sequence_id.prefix and \
                    journal_current.sequence_id.prefix[:1] == invoice_prefix) and \
                        ((not currency_id) or ((not journal_current.currency_id and currency_id == 'CURRENCY_COMPANY') or \
                                               journal_current.currency_id and currency_id == journal_current.currency_id)):
                    journal_selected = journal_current

                if journal_selected:
                    result_dict.update(journal_id=journal_selected.id)
                else:
                    type_domain = 'sale' if self._context.get(
                        'type') == 'out_invoice' or self.move_type == 'out_invoice' else 'sale_refund'
                    for journal in self.env['account.journal'].search([('type', '=', type_domain)]):
                        if type_domain == 'sale':
                            if is_note_document:
                                if journal.sunat_document_type.code != u'08':
                                    continue
                            else:
                                if journal.sunat_document_type.code == u'08':
                                    continue

                        journal_temp = [0, journal]
                        if journal.sequence_id and journal.sequence_id.prefix and journal.sequence_id.prefix[
                                                                                  :1] == invoice_prefix:
                            journal_temp[0] = 1

                        if currency_id and (currency_id == journal.currency_id):
                            journal_temp[0] = journal_temp[0] + 1

                        if journal_temp[0] == 2:
                            journal_selected = journal_temp
                            break

                        if not journal_selected:
                            if journal_temp[0] > 0:
                                journal_selected = journal_temp
                        elif journal_selected[0] < journal_temp[0]:
                            journal_selected = journal_temp

                    if journal_selected:
                        result_dict.update(journal_id=journal_selected[1].id)

            type_related_documents = self.env['peb.catalogue.01'].search([('code', 'in', ['01', '03'])])

            # Al no tener una columna de prefijo en el catálogo, nos basaremos en la columna descripción, lo cual no
            # es un valor seguro para realizar esta operación ya que podrían cambiar el valor de la descripción.
            for trd in type_related_documents:
                if trd.description[:1] == invoice_prefix:
                    #result_dict.update(type_related_document=trd.id)
                    result_dict.update(related_document_type=trd.code)
                    break

        return dict(value=result_dict)

    @api.onchange('reason')
    def onchange_reason(self):
        reason = self.reason
        if reason and self.move_type == 'out_invoice':
            result_dict = dict(invoice_id_not_required=False)
            irt_obj = self.env['peb.catalogue.09'].browse(reason.id)
            if irt_obj.code == '03':
                result_dict.update(invoice_id_not_required=True)
            return dict(value=result_dict)

    is_note_document = fields.Boolean(default=False)
    invoice_id_not_required = fields.Boolean(default=False)    