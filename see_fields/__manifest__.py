# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Hidde fields product',
    'summary': 'Ver campos de productos ocultos por variante',

    'description': """
    Ver campos de productos ocultos por variante
    """,
    'author': "Xmarts, Nayeli Valencia Díaz",
    'website': "http://www.xmarts.com",
    'depends': ['base','product','stock_account','product_margin'],
    'data': [
        'views/views.xml',
'views/templates.xml',
    ]
}
