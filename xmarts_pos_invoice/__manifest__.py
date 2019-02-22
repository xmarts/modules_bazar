# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Facturacion Globales de POS',
    'summary': 'Facturacion Globales',

    'description': """
    Facturacion Globales de POS
    """,
    'author': "Xmarts, Luis Alfredo Valencia Díaz",
    'website': "http://www.xmarts.com",
    'depends': ['base','point_of_sale',"product",
                "sale",
		        "account","l10n_mx_edi"],
    'data': [
        'views/pos_invoice_view.xml',
        'views/pos_order_view_10.xml',
        'views/views.xml',
    ]
}
