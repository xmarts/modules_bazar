# -*- coding: utf-8 -*-
{
    'name': "loadseries",

    'summary': """
        Modulo de carga de series y actualizacion de series V11""",

    'description': """
       Modulo de carga de series y actualizacion de series para Odoo 11
    """,

    'author': "Nayeli Jazmin Valencia Diaz",
    'website': "http://www.xmarts.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','purchase','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}