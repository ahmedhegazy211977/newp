# -*- coding: utf-8 -*-
{
    'name': "Leajlak Delivery",

    'summary': "Connect odoo with Laglak delivery",

    'description': """
        Connect odoo with Laglak delivery
    """,

    'author': "Majed Shogaa",
    'website': "majedshogaa@gmail.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website_sale','stock','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/delivery_carrier.xml',
        'views/stock_picking.xml',
        'views/template.xml',
        'views/sale_order.xml',
        'data/data.xml',
        'views/res_country_state.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'license': "AGPL-3",
}

