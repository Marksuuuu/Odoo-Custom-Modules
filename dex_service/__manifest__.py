# -*- coding: utf-8 -*-
{
    'name': "Dex Odoo Service",

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
    'depends': ['base', 'hr', 'account', 'product', 'sale'],

    # always loaded

    'data': [
        ## Security ##
        
        'security/groups.xml',
        'security/security.xml',
        
        ## Report ##
        'views/reports/menu/menu.xml',
        'views/reports/service_report.xml',
        
        ## Wizard ##
        
        'wizard/create_thread_wizard.xml',
        'wizard/block_reason.xml',
        'wizard/create_ticket_by.xml',
        # 'wizard/assign_request.xml',
        'wizard/client_search.xml',
        'wizard/print_service_report.xml',
        'wizard/transfer_to.xml',
        
        ## Views ##
        'views/inherit/sale_order.xml',
        'views/assign_request.xml',
        'views/warranty.xml',
        'views/sequence/sequence.xml',
        'views/service_line_thread_view.xml',
        'views/service_line_view.xml',
        'views/menu/menu.xml',
        'views/service_view.xml',
        'views/not_existing_product.xml',

    ],
    'qweb': [
        'static/src/xml/custom_button_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dex_service/static/src/js/custom_button_widget.js',
            # 'dex_service/static/src/js/form_handler.js',
        ],
    },
    'installable': True,

}
