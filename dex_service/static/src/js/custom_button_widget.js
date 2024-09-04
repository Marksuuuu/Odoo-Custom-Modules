odoo.define('dex_service.CustomButtonWidget', function (require) {
    'use strict';

    var core = require('web.core');
    var FormView = require('web.FormView');
    var Widget = require('web.Widget');

    var CustomButtonWidget = Widget.extend({
        template: 'CustomButtonTemplate',

        events: {
            'click .o_custom_button': '_onButtonClick',
        },

        init: function (parent, params) {
            this._super(parent);
            this.numberField = params.numberField || 'count_field';  // Default field name
        },

        start: function () {
            this._super.apply(this, arguments);
            this._fetchNumberFromField();
        },

        _fetchNumberFromField: function () {
            var self = this;
            this.trigger_up('get_field_value', { field: this.numberField }).then(function (value) {
                self.number = value;
                self.$el.find('.o_custom_button span').text(value);
            });
        },

        _onButtonClick: function () {
            this.trigger_up('button_clicked', { number: this.number });
        },
    });

    core.form_widget_registry.add('custom_button_widget', CustomButtonWidget);

    return CustomButtonWidget;
});
