odoo.define('your_module_name.redirect', function (require) {
    "use strict";

    var core = require('web.core');
    var WebClient = require('web.WebClient');
    var session = require('web.session');

    WebClient.include({
        start: function () {

            var self = this;
            console.log(self)
            this._super.apply(this, arguments);

            // Replace 'your_model_name' and 'your_form_view_id' with the actual model and form view ID
            var model = 'your_model_name';
            var viewId = 'your_form_view_id';

            // Redirect to the specific form view after login
            if (session.uid && this.action_manager) {
                this.action_manager.do_action({
                    type: 'ir.actions.act_window',
                    res_model: model,
                    views: [[viewId, 'form']],
                    target: 'current',
                });
            }
        },
    });
});
