from odoo import models,fields,api

class Reporte(models.TransientModel):
    _name="wizard_report"

    date_from=fields.Date(string="Inicio")
    date_to=fields.Date(string="Hasta")


    def get_report_xlsx(self):
        data={
            'date_from':self.date_from,
            'date_to':self.date_to
        }
        return self.env.ref('conastec.action_report_wizard').report_action(self,data=data)