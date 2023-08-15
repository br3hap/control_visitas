# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from io import BytesIO
import pytz
import xlsxwriter
import base64
from datetime import datetime, date, timedelta
from pytz import timezone
import logging
_logger = logging.getLogger(__name__) 



class mod_request_liquidation_sheet_export(models.Model):
    _inherit = 'mod.request.liquidation.sheet'
    _description = _("Mod Request Liquidation Export Excel")

    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone('America/Lima'))

    file_data = fields.Binary('File', readonly=True)


    def cell_format(self, workbook):
        cell_format = {}
        cell_format['title'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 25,
            'font_name': 'Arial',
            # 'bg_color':'#EDED0A',
        })
        cell_format['no'] = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': True
        })
        cell_format['header'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            # 'bg_color':'#0BBB20',
            'border': True,
            'font_name': 'Arial'
        })
        cell_format['content'] = workbook.add_format({
            'font_size': 11,
            'border': True,
            'font_name': 'Arial'
        })
        cell_format['content_float'] = workbook.add_format({
            'font_size': 11,
            'border': True,
            'num_format': '#,##0.00',
            'font_name': 'Arial',
        })
        cell_format['total'] = workbook.add_format({
            'bold': True,
            # 'bg_color':'#CDCD08',
            'num_format': '#,##0.00',
            'border': True,
            'font_name': 'Arial'
        })
        return cell_format, workbook


    def action_export_requirements_to_excel(self):
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        cell_format, workbook = self.cell_format(workbook)
        report_name = _('Liquidaciones')
        worksheet = workbook.add_worksheet(report_name)
        now = datetime.now() - timedelta(hours=5)

        columns = [
            _('CLIENTE'),
            _('GRUPO O DEUDOR PRINCIPAL AL QUE PERTENECE'),
            _('CASO'),
            _('DEMANDANTE/DEMANDADO DEL CASO'),
            _('N° EXPEDIENTE'),
            _('N° EXPEDIENTE ADMINISTRATIVO(ANTECEDENTES)'),
            _('TIPO DEL PROCESO'),
            _('MATERIA DEL PROCESO'),
            _('ABOGADO A CARGO / FUNCIONARIO'),
            _('TIPO O AREA DE BANCA'),
            _('N° DE CUENTA O CONTRATO(20 DIGITOS)'),
            _('TIPO DE PRODUCTO'),
            _('TIPO DE RAMO'),
            _('TIPO DE SEGURO'),
            _('CODIGO DE PRODUCTO'),
            _('CODIGO ERP'),
            _('N° IDC'),
            _('N° SINIESTRO'),
            _('TIPO DE GASTO'),
            _('DESCRIPCION DEL GASTO'),
            _('SITE'),
            _('JUZGADO/ENTIDAD'),
            _('N° DE DOCUMENTO'),
            _('PROVEEDOR'),
            _('RUC DE PROVEEDOR'),
            _('FECHA DE COMPROBANTE'),
            _('TIPO DE COMPROBANTE'),
            _('TIPO DE MONEDA'),
            _('IMPORTE DE GASTO'),
            _('FIRMA/OBSERVACIONES'),
        ]

        column_length = len(columns)
        if not column_length:
            return False
        
        no = 1
        column = 1

        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 40)
        worksheet.set_column('D:E', 40)
        worksheet.set_column('F:AE', 30)
        worksheet.merge_range(0, 0, 1, column_length,
                              report_name, cell_format['title'])
        worksheet.merge_range('A4:C4', _('Export Date: %s') %
                              now, cell_format['total'])
        worksheet.write('A6', 'No', cell_format['header'])
        
        for col in columns:
            worksheet.write(5, column, col, cell_format['header'])
            column += 1

        data_list = []

        for rec in self.browse(self._context.get('active_ids')):
            for l in rec.line_ids:
                data_list.append([
                    l.partner_id.name or '',
                    '',
                    l.case or '',
                    '',
                    l.proceedings or '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    l.court_entity or '',
                    l.ruc_dni or '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    l.amount,
                    ''
                ])
        
        row = 7
        column_float_number = {}

        for data in data_list:
            worksheet.write('A%s' % row, no, cell_format['no'])
            no += 1
            column = 1
            for value in data:

                if type(value) is int or type(value) is float:
                    content_format = 'content_float'
                    column_float_number[column] = column_float_number.get(
                        column, 0) + value
                else:
                    content_format = 'content'

                if isinstance(value, datetime):
                    value = pytz.UTC.localize(value).astimezone(
                        timezone(self.env.user.tz or 'UTC'))
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, date):
                    value = value.strftime('%Y-%m-%d')

                worksheet.write(row - 1, column, value,
                                cell_format[content_format])
                column += 1

            row += 1

        row -= 1


        for x in range(column_length + 1):

            if x == 0:
                worksheet.write('A%s' % (row + 1), _('Total'),
                                cell_format['total'])
            elif x not in column_float_number:
                worksheet.write(row, x, '', cell_format['total'])
            else:
                worksheet.write(
                    row, x, column_float_number[x], cell_format['total'])

        workbook.close()

        result = base64.encodebytes(fp.getvalue()).decode('utf-8')
        date_string = self.get_default_date_model().strftime("%Y-%m-%d")
        filename = '%s %s' % (report_name, date_string)
        filename += '%2Exlsx'
        self.write({'file_data': result})

        url = "web/content/?model=" + self._name + "&id=" + str(
            self[:1].id) + "&field=file_data&download=true&filename=" + filename

        return {
            'name': _('Generic Excel Report'),
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
        
        _logger.warning('export')