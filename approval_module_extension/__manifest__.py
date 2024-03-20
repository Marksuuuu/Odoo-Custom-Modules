# -*- coding: utf-8 -*-
{
    'name': "Approval Module",
    'sequence': 0,

    'summary': """
       Approval Module Extension For Odoo 13""",

    'website': "https://www.teamglac.com/",

    'description': """
        Approval Module Extension 
        
        Ⓒ. 2023-2024
    """,

    'author': "Alex Fernan Mercado / John Raymark LLavanes",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Extension',
    'version': '6.9',

    # any module necessary for this one to work correctly
    'depends': ['account', 'purchase', 'stock', 'purchase_stock', 'om_account_accountant', 'om_account_asset',
                'om_account_budget',
                'team_accounting', 'accounting_pdf_reports', 'mrp', 'sale', 'purchase_requisition', 'approval_module',
                'delivery'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_requisition_view.xml',
        'views/purchase_order_view.xml',
        'views/stock_picking.xml',
        'views/stock_move.xml',
        'views/stock_scrap.xml',
        'views/inherit_purchase_requisition_view.xml',
        'reports/menu/report_menu.xml',
        'reports/purchase_requests_form.xml',
        'reports/invoice_voucher.xml',
        'reports/picking_operations.xml',
        'reports/purchase_order_form.xml',
        'wizard/change_approver_views.xml',
        'wizard/change_pr_approvers_views .xml',
        'wizard/disapprove_reason_views.xml',
        'wizard/disapprove_pr_reason_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
