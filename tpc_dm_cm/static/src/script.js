odoo.define('tpc_dm_cm.script', function (require) {
    "use strict";

    var WebClient = require('web.WebClient');

    WebClient.include({
        start: function () {
            this._super.apply(this, arguments);

            // Set a flag in the action context to indicate a reload
            this._rpc({
                model: 'ir.ui.menu',
                method: 'read',
                args: [this.menu_id],
                kwargs: { fields: ['id'] },
            }).then(function (result) {
                if (result && result.length > 0) {
                    var action = result[0];
                    if (action && action.context) {
                        action.context.trigger_on_reload = true;
                    }
                }
            });

            // Bind the function to the 'beforeunload' event
            $(window).on('beforeunload', this.proxy('onBeforeUnload'));

            // Trigger the Python function
            this.triggerPythonFunction();
        },

        onBeforeUnload: function () {
            // Your custom function to be triggered before the browser is unloaded
            this.triggerBeforeUnload();
        },

        triggerBeforeUnload: function () {
            // Your custom code to be executed before the browser is unloaded
        },

        triggerPythonFunction: function () {
            // Trigger the Python function on the server
            this._rpc({
                model: 'tpc.dm.cm',  // Replace with the actual model name
                method: 'kanban_data',
            });
        },
    });

});
