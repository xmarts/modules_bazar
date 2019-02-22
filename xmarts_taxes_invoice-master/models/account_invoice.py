
from openerp import models, fields, api, _, tools
from openerp.exceptions import UserError, RedirectWarning, ValidationError

import logging
_logger = logging.getLogger(__name__)
class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    @api.multi
    def _l10n_mx_edi_create_taxes_cfdi_values(self):
        '''Create the taxes values to fill the CFDI template.
        '''
        self.ensure_one()
        values = {
            'total_withhold': 0,
            'total_transferred': 0,
            'withholding': [],
            'transferred': [],
        }
        for tax in self.tax_line_ids.filtered('tax_id'):
            tax_dict = {
                'name': (tax.tax_id.tag_ids[0].name
                if tax.tax_id.tag_ids else tax.tax_id.name).upper(),
                'amount': round(abs(tax.amount or 0.0), 2),
                'rate': round(abs(tax.tax_id.amount), 2),
                'type': tax.tax_id.l10n_mx_cfdi_tax_type,
            }
            if tax.amount >= 0:
                values['total_transferred'] += round(abs(tax.amount or 0.0), 2)
                values['transferred'].append(tax_dict)
            else:
                values['total_withhold'] += abs(tax.amount or 0.0)
                values['withholding'].append(tax_dict)
        a = self._validate_taxes()
        if a[0] != values['total_withhold']:
            values['total_withhold'] = a[0]
            values['withholding'][0]['amount'] = a[0]
        if a[1] != values['total_transferred']:
            values['total_transferred'] = a[1]
            values['transferred'][0]['amount'] = a[1]
        return values


    def _validate_taxes(self):
        amount_trans = 0
        amount_with = 0
        values = []
        for lines in self.invoice_line_ids:
            for tax_line in lines.invoice_line_tax_ids:
                if tax_line.amount < 0:
                    amount = round(tax_line.amount / 100.0 * lines.price_subtotal, 2)
                    amount_with += amount
                else:
                    amount = round(abs(tax_line.amount / 100.0 * lines.price_subtotal),2)
                    amount_trans += amount
        values.append(abs(amount_with))
        values.append(abs(amount_trans))
        return values