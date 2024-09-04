odoo.define('dex_service.FormHandler', function (require) {
    'use strict';

    var FormView = require('web.FormView');
    var core = require('web.core');
    var _t = core._t;

    FormView.include({
        start: function () {
            this._super.apply(this, arguments);
            var self = this;

            this.$el.on('button_clicked', function (event, data) {
                console.log('Button clicked with number:', data.number);
                // Perform actions based on the button click
                self._onButtonClicked(data.number);
            });

            this.$el.on('get_field_value', function (event, data) {
                var field = self.model.get(data.field);
                event.stopPropagation();
                if (field) {
                    self._rpc({
                        model: self.modelName,
                        method: 'read',
                        args: [[self.res_id], [data.field]],
                    }).then(function (result) {
                        event.data = result[0][data.field];
                        self.$el.trigger('get_field_value', event);
                    });
                }
            });
        },

        _onButtonClicked: function (number) {
            // Define what should happen when the button is clicked
        },
    });
});
