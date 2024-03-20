odoo.define('tpc_priority_list.priority_list_script', function (require) {
    "use strict";

    console.log("Module Loaded");

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;

    var TpcPriorityList = AbstractAction.extend({
        template: 'Dashboard',

        init: function (parent, context) {
            this._super.apply(this, arguments);
            console.log("Dashboard Initialized");

            // Initialize this.$el if not already defined
            this.$el = this.$el || $('<div>');

            // Fetch data using the priority_list_query method
            var self = this;
            this._rpc({
                model: 'tpc.priority.list',
                method: 'priority_list_query',
            }).then(function (data) {
                // Pass the fetched data to the template
                self.data = data;
                self.render();
            });
        },

        start: function () {
            // Perform additional initialization or actions after rendering
            console.log("Dashboard Started");
            return this._super.apply(this, arguments);
        },

        render: function () {
            var self = this;
                   var self = this;
                   self._rpc({
                       model: 'tpc.priority.list',
                        method: 'priority_list_query',
                       args: [],
                   }).then(function(datas) {
                   console.log("dataaaaaa", datas)
                       self.$('.table_view').html(QWeb.render('PriorityListData', {
                                  report_lines : datas,
                       }));
                   });
        },
    });

    core.action_registry.add("tpc_priority_list", TpcPriorityList);
    return TpcPriorityList;
});
