# -*- coding: utf-8 -*-
{
    'name': "Googel Geo Location",

    'summary': "This module to connect google geo location with odoo",

    'description': """
        This module to connect google geo location with odoo
    """,

    'author': "majedshogaa",
    'website': "majedshogaa@gmail.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website_sale'],

    # always loaded
    'data': [
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}

