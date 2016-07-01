# -*- coding: utf-8 -*-
{
    'name': "Hoc Rent",

    'summary': """Rental module, still in development""",

    'description': """
    This module's aim is to propose a rental system for little business, with reservation and calendar. 
            
    """,

    'author': "hoccau ",

    'website': "https://kidivid.org",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','website'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views/mainview.xml',
        'views/product.xml',
        'views/website_rental.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}


