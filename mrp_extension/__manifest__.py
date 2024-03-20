# -*- coding: utf-8 -*-
{
    'name': "mrp_extension",
    'sequence': 0,
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'mrp', 'sale'],

    # always loaded
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Views
        'views/product_template_views.xml',
        'views/test.xml',
        'views/sale_views.xml',
        'views/mrp_production_views.xml',

        # Reports
        'reports/mrp_production_templates.xml',
        'reports/mrp_report_views_main.xml',

    ],
    'application': True,

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
