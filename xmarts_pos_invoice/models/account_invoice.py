# -*- coding: utf-8 -*-
from openerp import api, fields, models, _, tools
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import datetime


class account_invoice_Inherit(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def invoice_validate(self):
        '''Generates the cfdi attachments for mexican companies when validated.'''
        result = super(account_invoice_Inherit, self).invoice_validate()
        version = self.l10n_mx_edi_get_pac_version()
        for record in self.filtered(lambda r: r.l10n_mx_edi_is_required()):
            if record.type == 'out_refund' and not record.refund_invoice_id.l10n_mx_edi_cfdi_uuid:
                record.message_post(
                    body='<p style="color:red">' + _(
                        'The invoice related has no valid fiscal folio. For this '
                        'reason, this refund didn\'t generate a fiscal document.') + '</p>',
                    subtype='account.mt_invoice_validated')
                continue
            record.l10n_mx_edi_cfdi_name = ('%s-%s-MX-Invoice-%s.xml' % (
                record.journal_id.code, record.number, version.replace('.', '-'))).replace('/', '')
            record._l10n_mx_edi_retry()
            #self._assign_payment_invoice_global()
        return result

    @api.multi
    def assign_payment_invoice_global(self):
        if self.state == 'open':
            if 'Factura Global' in self.origin:
                pos_order = self.env['pos.order'].search([('invoice_id','=',self.id)])
                payment_type = self.type in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
                if payment_type == 'inbound':
                    payment_method = self.env.ref('account.account_payment_method_manual_in')
                else:
                    payment_method = self.env.ref('account.account_payment_method_manual_out')
                vals = {
                    'invoice_ids': [(6, 0, self.ids)],
                    'amount' : self.residual,
                    'journal_id' : 12,
                    'payment_date' : datetime.datetime.now(),
                    'communication': self.number,
                    'partner_id': self.partner_id.id,
                    'partner_type': self.type in ('out_invoice', 'out_refund') and 'customer' or 'supplier',
                    'payment_type': payment_type,
                    'payment_method_id': payment_method.id
                 }
                payment = self.env['account.payment'].create(vals)
                payment.post()
