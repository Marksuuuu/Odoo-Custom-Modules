odoo.define('dex_service.tree_button', function (require) {
"use strict";
   var ListController = require('web.ListController');
   var ListView = require('web.ListView');
   var viewRegistry = require('web.view_registry');
   var TreeButton = ListController.extend({
      buttons_template: 'ServiceAssignButton',
      events: _.extend({}, ListController.prototype.events, {
          'click .open_wizard_action': '_OpenWizard',
      }),
      _OpenWizard: function () {
          var self = this;
           this.do_action({
              type: 'ir.actions.act_window',
              res_model: 'dex_service.service.main',
              name :'Assign',
              view_mode: 'form',
              view_type: 'form',
              views: [[false, 'form']],
              target: 'new',
              res_id: false,
          });
      }
   });
   var SaleOrderListView = ListView.extend({
      config: _.extend({}, ListView.prototype.config, {
          Controller: TreeButton,
      }),
   });
   viewRegistry.add('button_in_tree', SaleOrderListView);   });