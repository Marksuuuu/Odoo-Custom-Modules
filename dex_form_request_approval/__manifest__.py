{
    'name': "Form Approvals",

    'summary': """
        
        """,

    'description': """
        
        """,

    'author': 'John Raymark LLavanes',
    'company': '',
    'website': "https://johnraymarksuuuu.github.io/",

    'category': 'Application',
    'application': True,
    'version': '13.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'hr', 'crm'],

    # always loaded

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/cancellation_reason_views.xml',
        'wizard/disapprove_reason_views.xml',
        'wizard/create_bill_wizard.xml',
        # 'views/menu/assets.xml',
        'views/menu/sequence.xml',
        'views/menu/menu.xml',
        'views/form_request_types.xml',
        'views/approver_setup.xml',
        'wizard/cancellation_reason_views.xml',
        'wizard/disapprove_reason_views.xml',
        'views/request_for_cash_advance.xml',
        'views/official_business_form.xml',
        'views/transport_network_vehicle_form_view.xml',
        'views/transport_network_vehicle_type_view.xml',
        'views/vehicle_type_view.xml',
        'views/hr_employee.xml',

        'views/it_request_form.xml',
        'views/on_line_purchases.xml',
        'views/client_pickup_permit.xml',
        'views/overtime_authorization_form.xml',
        'views/gasoline_allowance_form.xml',
        'views/payment_request_form.xml',
        'views/grab_request_form.xml',
        'views/res_config_settings.xml',
        'views/preview_dashboard.xml',
        'views/account_move.xml',

        ## Report
        'reports/menu/paper_types.xml',
        'reports/menu/report_menu.xml',
        'reports/overtime_authorization_form_report.xml',
        'reports/official_business_form_report.xml',
        'reports/it_request_form_report.xml',
        'reports/gasoline_allowance_form_report.xml'

    ],
    'installable': True,

}
# -*- coding: utf-8 -*-
