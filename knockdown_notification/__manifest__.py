{

    'name': "Schedule",

    'summary': """
        Set Schedule for Notif
        ===========
            """,

    'author': "John Raymark LLavanes",
    'website': "",

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/menu/menu.xml',
        'views/set_schedule_view.xml'

    ],
    'license': 'LGPL-3',
}
# pylint: disable=manifest-required-author
