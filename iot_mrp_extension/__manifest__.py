# -*- coding: utf-8 -*-

{
    'name': "Internet of Thing to MRP",

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
        # 'security/ir.model.access.csv',
        # 'views/menu/menu.xml',
        # 'views/priority_list_view.xml',
        'views/main_template.xml',
        'views/templates.xml',
        'views/index.xml',
    ],

}
