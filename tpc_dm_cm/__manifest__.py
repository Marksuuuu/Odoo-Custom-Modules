# -*- coding: utf-8 -*-
{
    'name': "Team Pacific Corporation Billing Request",

    'summary': """
        Over the past year, Team Pacific Corporation has adeptly managed financial transactions through the strategic use of the Debit Memo (DM) and Credit Memo (CM). The Debit Memo serves as a meticulous record-keeping tool, ensuring transparency and accountability in financial dealings. Meanwhile, the Credit Memo reflects the team's commitment to customer satisfaction by facilitating fair adjustments, issuing refunds, and recognizing credits when necessary. Together, these financial instruments have been instrumental in guiding Team Pacific Corporation towards a successful and principled first year. 🚀💳""",

    'description': """
        Team Pacific Corporation has navigated the complexities of financial transactions with precision over the past year, employing the Debit Memo (DM) and Credit Memo (CM) as integral tools.

The Debit Memo (DM) serves as a reliable record-keeping instrument, meticulously documenting financial obligations and discrepancies. This tool has played a crucial role in maintaining the team's financial integrity and transparency.

On the other hand, the Credit Memo (CM) reflects the team's commitment to fairness and customer satisfaction. By issuing refunds or recognizing credits when necessary, the team utilizes the Credit Memo to uphold high standards of customer service and nurture positive relationships.

Together, the DM and CM stand as the cornerstone of Team Pacific Corporation's financial strategy. As the team marks its first year, here's to continued success and growth in the realm of financial excellence. 🚀💳
    """,
    'author': 'John Raymark LLavanes - 10450 (2023)',
    'company': 'Team Pacific Corporation',
    'website': "https://www.teamglac.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'application',
    'version': '0.10.69',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'approval_module', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/menu/menu.xml',
        'views/tpc_dm_cm.xml',
        'views/assets.xml',
        'views/file_type_view.xml',
        'views/res_config_settings_views.xml',
        'views/tpc_dm_cm_request.xml',
        'views/menu/sequence.xml',
        'views/menu/mail_cron.xml',
        'views/tpc_dm_cm_particulars.xml',
        'views/email_control_view.xml',
        'views/source_trade_non_trade.xml',
        'views/tpc_dm_cm_request_kanban.xml',
        'views/account_move.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
