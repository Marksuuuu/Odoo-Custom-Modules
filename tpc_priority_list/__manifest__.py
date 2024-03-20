# -*- coding: utf-8 -*-

{
    'name': "Priority List",

    'summary': """
        PRIORITY LIST MODULE
        """,

    'description': """
        PRIORITY LIST MODULE
        """,

    'author': 'John Raymark LLavanes - 10450 (2024)',
    'company': 'Team Pacific Corporation',
    'website': "https://www.teamglac.com/",

    'category': 'Application',
    'application': True,
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'sale'],

    # always loaded

    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/priority_list_script_view.xml',
    ],
    'qweb':[
        'static/src/xml/priority_list_view.xml'
    ],
    'installable': True,

}
