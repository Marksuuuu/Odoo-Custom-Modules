# John Raymark LLavanes
# MIS - 2k23
{
    'name': 'Team Pacific Corporation Freight Module',
    'version': '0.1',
    'category': 'Inventory Extensions',
    'summary': 'Freight Module Odoo 13',
    'sequence': '10',
    'author': 'John Raymark LLavanes - 10450',
    'company': 'Team Pacific Corporation',
    'maintainer': 'MIS - LOC 267',
    'support': 'mis@teamglac.com',
    'website': '',
    'depends': ['stock', 'account'],
    'live_test_url': '',
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_freight_view.xml',
        # 'data/freight_cron.xml',
        # 'views/freight_cron_view.xml',
        'views/freight_domain_sequence.xml',
        'views/mrp_freight_line_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [
        'static/src/xml/report_pdf_options.xml'
    ],
}
