from odoo import http
from odoo.http import request




class HeaderCustomController(http.Controller):

    @http.route('/header_custom/fetch_exchange_rate', type='json', auth='public')
    def fetch_exchange_rate(self):
        # Aquí puedes implementar la lógica para obtener el tipo de cambio desde una fuente externa o base de datos
        # Por simplicidad, se devuelve un valor estático en este ejemplo
        return '1.5'  # Cambia esto al valor real del tipo de cambio
    

    def request_search(self):
        values = {
            "name":"Breithner",
            "lastname":"Aquituari Pua"
        }
        return values
    


    @http.route('/api/request',type='json', auth='public', cors="*")
    def api_request(self, **kw):
        response_request = []
        response_request = self.request_search()
        return response_request
        # return request.render('header_custom.index',{
        #     'teachers':["Breithner Aquituari","Alondra Soto", "Genesis Campos"],
        # })
        # return "Hello, Breithner"
        # return request.render("header_custom.template_id",{})
        # Hacer una solicitud GET a la API de Rick and Morty
        # url = "https://rickandmortyapi.com/api/character"
        # response = request.get(url)
        # if response.status_code == 200:
        #     data = json.loads(response.text)
        #     data = json
        # character_count = data['info']['count']
        # return request.render("header_custom.template_id",{})