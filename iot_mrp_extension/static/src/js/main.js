odoo.define('iot_mrp_extension.main', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.your_search_handler = publicWidget.Widget.extend({
        selector: '.oe_form',

        start: function () {
            this.$el.on('submit', 'form.oe_form', this.proxy('searchSubmitted'));
            return this._super.apply(this, arguments);
        },

        searchSubmitted: function (ev) {
            ev.preventDefault();
            var searchInput = this.$('input[name="search_input"]').val();

            this._rpc({
                route: '/lms-login',
                params: { search_input: searchInput }
            }).then(this.handleResponse.bind(this)).guardedCatch(this.handleRPCError.bind(this));
        },

        handleResponse: function () {
            console.log('Search completed');
            // Handle the response as needed
            // For example, you can handle a successful search or redirect
        },

        handleRPCError: function (error) {
            console.error('RPC error:', error);
            // Handle RPC errors here
        },
    });

    return {
        your_search_handler: publicWidget.registry.your_search_handler,
    };
});
