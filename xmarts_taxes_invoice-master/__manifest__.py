# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Ajuste de Factura de decimales',
    'summary': 'Ajuste de decimales en las facturas',

    'description': """
    Ajuste de decimales en las facturas.
    """,
    'author': "Xmarts, Luis Alfredo Valencia Díaz",
    'website': "http://www.xmarts.com",
    'depends': ['l10n_mx_edi','account'],
    'data': [
        'data/3.3/cfdi.xml',
    ]
}
