# -*- coding: utf-8 -*-
{
    'name': "Dex Job Request Form",

    'summary': """
        
        """,

    'description': """
        
        """,

    'author': 'John Raymark LLavanes',
    'company': '',
    'website': "",

    'category': 'Application',
    'application': True,
    'version': '13.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'dex_form_request_approval', 'stock_warehouse_transfer', 'dex_whtransfer'],

    # always loaded

    'data': [
        'wizard/change_workers.xml',
        'security/groups.xml',
        'security/security.xml',
        'views/menu/menu.xml',
        'reports/menu/menu.xml',
        'reports/job_request_report.xml',
        'views/sequence/sequence.xml',
        'views/warehouse_order.xml',
        'views/job_request_view.xml'

    ],
    'installable': True,

}
