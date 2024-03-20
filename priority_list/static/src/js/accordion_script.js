odoo.define('priority_list.accordion', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var QWeb = core.qweb;

    var AccordionWidget = Widget.extend({
        template: 'AccordionWidget',
        init: function (parent, widget_data) {
            this._super.apply(this, arguments);
            this.widget_data = widget_data;
        },
    });

    core.action_registry.add('accordion_view', AccordionWidget);

    return AccordionWidget;
});
