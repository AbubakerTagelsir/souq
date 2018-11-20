# -*- coding: utf-8 -*-
{
    'name': "souq",

    'summary': """
        Demo for Online platform to trade various Products between end-userss""",

    'description': """
        this module is for Learning Purposes only
    """,

    'author': "Palmyra Solutions",
    'website': "http://www.palmyra-it.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'E-commerce',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'reports/order_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application':True,
}