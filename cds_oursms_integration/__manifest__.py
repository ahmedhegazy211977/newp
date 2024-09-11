# -*- coding: utf-8 -*-
{
    'name': "CDS OurSMS  Integration",
    'summary': """
        Integrate Odoo with Our-SMS SMS Gateway
    """,
    'description': """
     Odoo SMS Integration With oursms.com SMS Gateway
    """,
    'author': "OurSMS,CDS Solutions SRL,Ramadan Khalil",
    'website': "www.cds-solutions.co",
    'contributors': [
        'Ramadan Khalil <rkhalil1990@gmail.com>',
    ],
    'price': 29,
    'currency': 'USD',
    'version': '17.0',
    'license': 'OPL-1',
    'images': ['static/description/banner.gif'],
    'depends': ['base', 'sms', 'account'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    "external_dependencies": {"python": ["requests"]},
}
