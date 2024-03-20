# -*- coding: utf-8 -*-
{
    'name': "Inventory Extension",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "John Raymark LLavanes - 2024(10450)",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Extension',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'delivery', 'account', 'team_accounting', 'product', 'stock'],

    'data': [
        'views/stock_picking.xml',
        'views/product_template.xml',
        'views/stock_move_line.xml',
        'views/mrp_production.xml',
    ],

}
