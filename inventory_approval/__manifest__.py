# -*- coding: utf-8 -*-
{
    'name': "Inventory Approval",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "John Raymark LLavanes - 10450 (2024)",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Extension',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'delivery', 'account', 'team_accounting', 'product', 'inventory_extension', 'purchase', 'purchase_requisition'],

    'data': [
        'security/ir.model.access.csv',
        'views/inherit_stock_picking.xml',
        'wizard/inventory_change_approver_views.xml',
        'wizard/inventory_change_pr_approvers_views.xml',
        'wizard/inventory_disapprove_pr_reason_views.xml',
        'wizard/inventory_disapprove_pr_reason_views.xml',
        'wizard/inventory_disapprove_reason_views.xml'
    ],

}
