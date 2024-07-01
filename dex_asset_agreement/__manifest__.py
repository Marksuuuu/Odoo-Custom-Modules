# -*- coding: utf-8 -*-
{
    'name': "Dex Assets Agreement",

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
    'depends': ['web', 'base', 'stock', 'dex_form_request_approval', 'stock_warehouse_transfer', 'dex_whtransfer'],

    # always loaded

    'data': [
        'security/groups.xml',
        'security/security.xml',
        'wizard/agreement_wizard.xml',
        'views/menu/menu.xml',
        'views/menu/web_digital_sign_view.xml',
        'views/sequence/sequence.xml',
        'views/agreement.xml',
        'views/asset.xml'

    ],
    'installable': True,
    "qweb": ["static/src/xml/digital_sign.xml"],
}
