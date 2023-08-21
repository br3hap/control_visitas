/** @odoo-module **/
console.log("sdsdsdsdsd entro")

var FormController = require('web.FormController');

    FormController.include({
        // Extiende la función _onButtonClicked para agregar tu lógica personalizada
        _onButtonClicked: function (event) {
            if (event.data.attrs.name === 'button_function') {
                // Lógica de JavaScript para el botón personalizado
                console.log("Botón personalizado clickeado desde el lado del cliente.");
            }
            this._super.apply(this, arguments);
        },
    });