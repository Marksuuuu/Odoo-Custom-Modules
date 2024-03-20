# -*- coding: utf-8 -*-

{
    'name': "Report Generation",

    'summary': """
        Report Generation
        """,

    'description': """
        Report Generation
        """,

    'author': 'John Raymark LLavanes - 10450 (2024)',
    'company': 'Team Pacific Corporation',
    'website': "https://www.teamglac.com/",

    'category': 'Application',
    'application': True,
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'sale', 'account', 'accounting_pdf_reports', 'sales_extension_module'],

    # always loaded

    'data': [
        'security/ir.model.access.csv',
        'views/menu/menu.xml',
        'views/account_move_inherit_view.xml',
        'views/report_template_setup_view.xml',
        'reports/menu/report_menu.xml',
        'reports/invoice_voucher_template_1.xml',
        'reports/invoice_voucher_template_2.xml',

    ],
    'installable': True,

}
