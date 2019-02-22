# -*- encoding: utf-8 -*-

from openerp import api, fields, models, _, tools, release
from openerp.exceptions import UserError


class pos_order(models.Model):
    _inherit = "pos.order"

    def get_customer_for_general_public(self):
        partner_obj = self.env['res.partner']
        partner_id = partner_obj.search([('use_partner_general', '=', True)], limit=1)
        if not partner_id:
            raise UserError(_('Por favor configure un cliente general.'))

        return partner_id

    @api.multi
    def search_product_global(self):
        product_temp = self.env['product.template'].search([('use_product_general','=',True)], limit=1)
        if not product_temp:
            raise UserError(_('No ha dado de alta ningun producto.'))
        product_id = self.env['product.product'].search([('product_tmpl_id','=',product_temp.id)], limit=1)
        return product_id

    def action_view_invoice(self, invoice_ids):
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.invoice_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'graph'], [False, 'kanban'],
                      [False, 'calendar'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_ids) > 1:
            result['domain'] = "[('id','in', [" + ','.join(map(str, invoice_ids)) + "])]"
        elif len(invoice_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = invoice_ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    @api.multi
    def action_invoice3(self, date):
        context = self._context
        if 'journal_id' in context:
            journal_id = context['journal_id']
        else:
            journal_id = False

        # if context is None: self._context = {}
        inv_ref = self.env['account.invoice']
        acc_tax_obj = self.env['account.tax']
        inv_line_ref = self.env['account.invoice.line']
        product_obj = self.env['product.product']
        bsl_obj = self.env['account.bank.statement.line']
        ### Busqueda del Cliente Publico en General ###
        general_public_partner = self.get_customer_for_general_public()
        tickets_to_set_as_general_public = []

        partner = self.get_customer_for_general_public()
        inv_ids = []
        po_ids = self.env['pos.order']
        lines = {}
        for order in self:
            if order.invoice_id:
                inv_ids.append(order.invoice_id.id)
                continue
            if not order.partner_id:
                order.partner_id = partner
            if not order.invoice_2_general_public:
                # print "order: %s - %s - %s" % (order.name, order.partner_id and order.partner_id.name or 'Sin Partner', order.invoice_2_general_public)
                res = order.action_pos_order_invoice()
                if res:
                    xinv = inv_ref.browse(res['res_id'])
                    inv_ids.append(res['res_id'])
            else:
                tickets_to_set_as_general_public += order
                currency_id = order.pricelist_id.currency_id.id
                company_id = order.company_id.id
                account_id = order.partner_id.property_account_receivable_id.id

        if tickets_to_set_as_general_public:
            lines_to_invoice = []
            global_origin_name = ""
            ### Busqueda del Producto para Facturacion ###
            global_product_id = tickets_to_set_as_general_public[0].search_product_global()

            ### Rertorno de la cuenta para Facturación ###
            account = global_product_id.property_account_income_id or global_product_id.categ_id.property_account_income_categ_id

            ticket_id_list = []
            for ticket in tickets_to_set_as_general_public:
                pos_reference = ticket.name if ticket.name else ticket.pos_reference
                global_origin_name += pos_reference + ","
                for line in ticket.lines:
                    lines_to_invoice.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': 'Venta del ticket: {}'.format(ticket.name),
                        'quantity': line.qty,
                        'account_id': account.id,
                        'uom_id': line.product_id.uom_id.id,
                        'invoice_line_tax_ids': [(6, 0, [x.id for x in line.tax_ids])],
                        'price_unit': line.price_unit,
                        'discount': line.discount,
                        # 'sale_line_ids': [(6,0,order_line_ids)]
                    }))

                ticket.write({'invoice_2_general_public': True, 'state': 'invoiced'})

                ### Escribiendo como Facturados los Pedidos ####
                # ticket.order_line.write({'invoice_status' : 'invoiced','invoice_count': 1})
                ticket_id_list.append(ticket.id)


            pay_method_ids = self.env['l10n_mx_edi.payment.method'].search([('code', '=', '01')])
            if not pay_method_ids:
                raise UserError("Error!\nNo se encuentra el metodo de Pago 01.")

            invoice_vals = {
                'partner_id': general_public_partner.id,
                'l10n_mx_edi_usage': 'P01',
                'l10n_mx_edi_payment_method_id': pay_method_ids.id,
                'journal_id': journal_id,
                'date_invoice': date,
                'invoice_line_ids': lines_to_invoice,
                'origin': 'Factura Global [ ' + global_origin_name + ' ]',
                'account_id': account_id,
                'company_id': company_id,
                'type': 'out_invoice',
                'currency_id': currency_id,
            }

            invoice_id = inv_ref.create(invoice_vals)

            # tickets_to_set_as_general_public.write({'invoice_id': invoice_id.id})
            self.env.cr.execute("""
                        update pos_order set invoice_id = %s where id in %s;
                        """, (invoice_id.id, tuple(ticket_id_list)))

            inv_ids.append(invoice_id.id)

            ## Reclasificacando Impuestos ##
            invoice_id.compute_taxes()
            #invoice_id.tax_line_ids.set_tax_cash_basis_account()
            msj = ""
            for order in self:
                ref = "<a href=# data-oe-model=pos.order data-oe-id={}>{}</a>".format(order.id, order.name)
                msj += ref+ ", "
            message = _(
                "Esta factura ha sido generada de les pedidos de pos: %s") % (
                      msj)
            invoice_id.message_post(body=message)

        if not inv_ids: return {}
        res = self.action_view_invoice(inv_ids)
        return res


class pos_order_invoice_wizard(models.TransientModel):
    _inherit = "pos.order.invoice_wizard"

    @api.multi
    def create_invoice_from_pos(self):
        general_public_partner = self.env['pos.order'].get_customer_for_general_public()
        tickets_to_set_as_general_public = ticket_ids = self.env['pos.order']
        res = {}
        for line in self.ticket_ids:
            ticket_ids += line.ticket_id
            if line.invoice_2_general_public:
                tickets_to_set_as_general_public += line.ticket_id
        # Ponemos todos los tickets a facturar como si no fueran Publico en General, esto por si se cancelo/elimino una Factura previa

        ticket_ids.write({'invoice_2_general_public': 0})
        # self._cr.execute("update pos_order set invoice_2_general_public=false where id IN %s",(tuple(ids_to_invoice),))
        if tickets_to_set_as_general_public:
            tickets_to_set_as_general_public.write({'invoice_2_general_public': 1})
            for ticket in tickets_to_set_as_general_public:
                ticket.statement_ids.write({'partner_id': general_public_partner.id})
                for statement in ticket.statement_ids:
                    move_ids = [account_move.id for account_move in statement.journal_entry_ids]
                    if move_ids:
                        self._cr.execute('update account_move set partner_id=%s where id IN %s;',
                                         (general_public_partner.id, tuple(move_ids),))
                        self._cr.execute('update account_move_line set partner_id=%s where move_id IN %s;',
                                         (general_public_partner.id, tuple(move_ids),))
        if release.major_version == "9.0":
            res = ticket_ids.action_invoice3(self.date, self.journal_id.id)
        elif release.major_version in ("10.0", "11.0"):
            context_to_invoice = {'journal_id': self.journal_id.id}
            res = ticket_ids.with_context(context_to_invoice).action_invoice3(self.date)
        return res or {'type': 'ir.actions.act_window_close'}
