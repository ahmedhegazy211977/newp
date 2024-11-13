# -*- coding: utf-8 -*-
{
    'name': "Branch Sales",

    'summary': "Branch Sales",

    'description': """
        Branch Sales
    """,

    'author': "Majed Hameed",
    'website': "https://ajabaa.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website_sale','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/mj_branch.xml',
        'views/delivery_carrier.xml',
        'views/sale_order.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}

