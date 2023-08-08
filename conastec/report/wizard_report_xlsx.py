from odoo import models,fields,exceptions
import logging
from logging import getLogger


_logger=getLogger(__name__)

class ReportXLSX(models.AbstractModel):
    _name="report.conastec.report_xlsx"
    _inherit='report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        _logger.info("****Testeando***")
        _logger.info(data)

        account_move=self.env['account.move'].search([('invoice_date','>=',data.get('date_from',False)),('invoice_date','<=',data.get('date_to',False))])

        sheet = workbook.add_worksheet('Reporte')
        format_1 = workbook.add_format(
            {
                'bold': True,
                'border':2,
                'align':'center',
            }
        )
        format_date=workbook.add_format(
            {
                'bold': True,
                'border':2,
                'align':'center',
                'num_format': 'yyyy-mm-dd'
            }
        )

        sheet.set_column('B:B',20)
        sheet.set_column('C:C',20)
        sheet.set_column('D:D',20)
        sheet.set_column('E:E',20)
        sheet.set_column('F:F',20)

        sheet.write(0, 1, 'Numero Factura',format_1)
        sheet.write(0, 2, 'Cliente',format_1)
        sheet.write(0, 3, 'Fecha Factura',format_1)
        sheet.write(0, 4, 'Total',format_1)
        sheet.write(0, 5, 'Estado',format_1)

        _logger.info(account_move)  
        row=0
        col=0
        if account_move:
            for a in account_move:
                sheet.write(row+1, col+1,a.name,format_1)
                sheet.write(row+1, col+2,a.invoice_partner_display_name,format_1)
                sheet.write(row+1, col+3,a.invoice_date,format_date)
                sheet.write(row+1, col+4,a.amount_total_signed,format_1)
                sheet.write(row+1, col+5,a.state,format_1)

                row+=1
            
        else:
            raise exceptions.ValidationError("!........ESTIMADO NO EXISTE REGISTROS CON ESAS FECHAS..........¡")
  