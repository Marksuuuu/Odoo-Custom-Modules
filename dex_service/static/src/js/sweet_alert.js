odoo.define('dex_service.sweet_alert', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var swal2 = window.Swal;

    var MyWidget = Widget.extend({
        start: function () {
            this._super.apply(this, arguments);
            this._performServerOperation();
        },

        _performServerOperation: function () {
            var self = this;
            rpc.query({
                model: 'dex.service.request.form',
                method: 'find_or_create_record',
                args: []
            }).then(function (result) {
                swal2.fire({
                    title: 'Success!',
                    text: 'The server-side operation completed successfully.',
                    icon: 'success',
                    confirmButtonText: 'OK'
                });
            }).catch(function (error) {
                swal2.fire({
                    title: 'Error!',
                    text: 'An error occurred: ' + error.message,
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            });
        },
    });

    core.action_registry.add('my_widget', MyWidget);
});
