# -*- coding: utf-8 -*-

{
    'name': "Sales Extension Module",

    'summary': """
        SALES EXTENSION MODULE""",

    'description': """
    SALES EXTENSION MODULE
    """,

    'author': 'John Raymark LLavanes - 10450 (2023)',
    'company': 'Team Pacific Corporation',
    'website': "https://www.teamglac.com/",


    'category': 'extension',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'delivery', 'account', 'team_accounting'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/menu/menu.xml',
        'views/account_move.xml',
        'views/sales.xml',
        'views/sales_product_view.xml',
        'reports/menu/report_menu.xml',
        'reports/travel_voucher.xml',
        # 'reports/invoice_voucher.xml',
        'reports/transfer_voucher.xml',
        'reports/debit_note_voucher.xml',
        'reports/payable_voucher.xml',
        'reports/test_payable_voucher.xml',
        'reports/debit_credit_note_voucher_without_fee.xml',
        'reports/credit_note_voucher.xml',
        'views/stock_picking.xml',
        'views/res_partner.xml',
        'views/templates.xml'
    ],
}
