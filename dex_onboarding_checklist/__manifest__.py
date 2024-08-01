# -*- coding: utf-8 -*-
{
    'name': "Dex Job Onboarding Checklist",

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
    'depends': ['base', 'hr', 'dex_form_request_approval'],

    # always loaded

    'data': [
        'security/groups.xml',
        'security/security.xml',
        'views/sequence/sequence.xml',
        'views/menu/menu.xml',
        'views/sequence/sequence.xml',
        'views/history_log.xml',
        'views/employee_onboarding_checklist.xml',

    ],
    'installable': True,

}
