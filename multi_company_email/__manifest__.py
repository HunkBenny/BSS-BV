# noinspection PyStatementEffect
{
    'name': "Multi Company Email / Multi Company Signature",

    'sequence': 202,

    'summary': """ Changes user's email and signature to the ones defined in the current company """,

    'author': "Arxi",
    'website': "http://www.arxi.pt",

    'category': 'Extra Tools',
    'version': '15.0.1.0.2',
    'license': 'OPL-1',

    'price': 99.00,
    'currency': 'EUR',

    'depends': ['base', 'mail'],

    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            'multi_company_email/static/src/js/composer_view.js',
        ],
    },

    'images': [
        'static/description/banner.png',
    ],

    'application': True,
    'installable': True,
    'post_init_hook': 'post_init_hook'
}
