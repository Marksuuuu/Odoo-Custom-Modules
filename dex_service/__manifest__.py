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
    'depends': ['base', 'hr', 'account', 'product', 'sale', 'website', 'web', 'dex_pricelist_update'],

    # always loaded

    'data': [
        ## Security ##

        'security/groups.xml',
        'security/security.xml',

        'wizard/dex_service_cancellation_request.xml',  ## Why is this wizard in this position? This wizard is responsible for cancellation requests, and I placed it here due to hierarchy issues. -->


        ## Views ##
        'views/assets.xml',
        'views/inherit/sale_order.xml',
        'views/dex_service_assign_request.xml',
        # 'views/templates.xml',
        'views/warranty.xml',
        'views/sequence/sequence.xml',
        'views/dex_service_service_line_thread_view.xml',
        'views/service_line_view.xml',
        'views/menu/menu.xml',
        'views/dex_service_not_existing_product.xml',
        'views/dex_service_request_form.xml',
        'views/cron/itinerary_configuration.xml',
        'views/cron/dex_service_cron.xml',
        'views/service_view.xml',
        'views/inherit/service.xml',
        'views/my_chart_views.xml',
        'views/dashboard_views.xml',

        ## Report ##

        # 'views/reports/menu/menu.xml',
        'views/reports/menu/menu.xml',
        'views/reports/service_report.xml',
        'views/reports/service_request_form.xml',
        'views/reports/acknowledgement_form.xml',

        ## Wizard ##

        'wizard/dex_service_add_service.xml',
        'wizard/dex_service_block_reason.xml',
        'wizard/dex_service_create_ticket_by.xml',
        'wizard/dex_service_client_search.xml',
        'wizard/dex_service_print_service_report.xml',
        'wizard/dex_service_transfer_to.xml',
        'wizard/dex_service_service_main.xml',
        # 'wizard/dex_service_create_thread_wizard.xml',
        'wizard/dex_service_create_thread_wizard.xml',

    ],
    'qweb': [
        "static/src/xml/tree_button.xml",
        "static/src/xml/chart_template.xml",
    ],
    'installable': True,

}
