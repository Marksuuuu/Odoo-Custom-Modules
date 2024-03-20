# pylint: disable=manifest-required-author
{

    'name': "Approvals",

    'summary': """
        Approvals
        ===========
        |This module is used if an approval is needed before a purchase order will be submitted
            """,

    'author': "Agile Software Solutions and Technologies OPC",
    'website': "https://agiletech.ph",


    # any module necessary for this one to work correctly
    'depends': ['account', 'purchase', 'stock', 'purchase_stock', 'om_account_accountant', 'om_account_asset', 'om_account_budget',
                'team_accounting', 'accounting_pdf_reports', 'mrp', 'sale', 'purchase_requisition'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/change_approver_views.xml',
        'wizard/change_pr_approvers_views .xml',
        'wizard/disapprove_reason_views.xml',
        'wizard/disapprove_pr_reason_views.xml',
        'views/css_styles.xml',
        'views/purchase_requisition_view.xml',
        'views/purchase_order_views.xml',
        'views/approval_types_views.xml',
        'views/department_approvers_views.xml',
        'views/change_approver_rsn_views.xml',
        'views/approval_views.xml',


    ],
    'license': 'LGPL-3',
}
