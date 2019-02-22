# -*- encoding: utf-8 -*-

from openerp import api, fields, models, _, tools
from openerp.exceptions import UserError

    
class pos_order(models.Model):
    _inherit = "pos.order"
    
    
    invoice_2_general_public = fields.Boolean(string='General Public', 
                                              help="Check this if this POS Ticket will be invoiced as General Public")

    @api.multi
    def search_product_global(self):
        for rec in self:
            product_uom = self.env['product.uom']
            product_obj = self.env['product.product']
            company = rec.company_id
            if not company.product_for_global_invoice:
                uom_id = product_uom.search([('name', '=', 'Actividad Facturacion')])
                uom_id = uom_id[0] if uom_id else False
                if not uom_id:
                    sat_udm = self.env['sat.udm']
                    sat_uom_id = sat_udm.search([('code', '=', 'ACT')])
                    if not sat_uom_id:
                        raise UserError("Error!\nNo existe la Unidad de Medida ACT.")
                    uom_id = product_uom.create({'sat_uom_id': sat_uom_id[0].id,
                                                 'name': 'Actividad Facturacion',
                                                 'category_id': 1})
                sat_product_id = self.env['sat.producto'].search([('code', '=', '01010101')])
                if not sat_product_id:
                    raise UserError("El Codigo 01010101 no existe en el Catalogo del SAT.")
                product_id = product_obj.search([('product_for_global_invoice', '=', True)])
                if product_id:
                    product_id = product_id[0]
                else:
                    product_id = product_obj.create({
                        'name': 'Servicio Facturacion Global',
                        'uom_id': uom_id.id,
                        'uom_po_id': uom_id.id,
                        'type': 'service',
                        'sat_product_id': sat_product_id[0].id,
                        'product_for_global_invoice': True,
                    })
                company.write({'product_for_global_invoice': product_id.id})
            else:
                product_id = company.product_for_global_invoice

            return product_id


class pos_order_invoice_wizard(models.TransientModel):
    _name = "pos.order.invoice_wizard"
    _description = "Wizard to create Invoices from several POS Tickets"

    @api.model  
    def default_get(self, fields):
        res = super(pos_order_invoice_wizard, self).default_get(fields)
        record_ids = self._context.get('active_ids', [])
        pos_order_obj = self.env['pos.order']
        if not record_ids:
            return {}
        tickets = []
        
        partner_id = pos_order_obj.get_customer_for_general_public().id

        for ticket in pos_order_obj.browse(record_ids):
            
            if ticket.state in ('cancel','draft') or (ticket.invoice_id and ticket.invoice_id.state != 'cancel'):
                continue
            flag = not bool(ticket.partner_id) or bool(ticket.partner_id.use_partner_general or ticket.partner_id.id == partner_id) or False
            tickets.append((0,0,{
                    'ticket_id'     : ticket.id,
                    'session_id'    : ticket.session_id.id,
                    'pos_reference' : ticket.pos_reference if ticket.pos_reference else ticket.name,
                    'user_id'       : ticket.user_id.id,
                    'partner_id'    : ticket.partner_id and ticket.partner_id.id or False,
                    'amount_total'  : ticket.amount_total,
                    'invoice_2_general_public' : flag,
                    }))
        res.update(ticket_ids=tickets)
        return res


    date       = fields.Datetime(string='Date', default=fields.Datetime.now(), required=True,
                              help='This date will be used as the invoice date and period will be chosen accordingly!')
    journal_id = fields.Many2one('account.journal', string='Invoice Journal', required=True,
                                  default=lambda self: self.env['account.journal'].search([('type', '=', 'sale'), ('company_id','=',self.env.user.company_id.id)], limit=1),
                                  help='You can select here the journal to use for the Invoice that will be created.')
    ticket_ids = fields.One2many('pos.order.invoice_wizard.line','wiz_id',string='Tickets to Invoice', required=True)


        
class pos_order_invoice_wizard_line(models.TransientModel):
    _name = "pos.order.invoice_wizard.line"
    _description = "Wizard to create Invoices from several POS Tickets2"

    wiz_id        = fields.Many2one('pos.order.invoice_wizard',string='Wizard', ondelete="cascade")
    ticket_id     = fields.Many2one('pos.order', string='POS Ticket')
    date_order    = fields.Datetime(related='ticket_id.date_order', string="Date", readonly=True)
    session_id    = fields.Many2one("pos.session", related='ticket_id.session_id', string="Session", readonly=True)
    pos_reference = fields.Char(related='ticket_id.pos_reference', string="Reference", readonly=True)
    user_id       = fields.Many2one("res.users", related='ticket_id.user_id', string="Salesman", readonly=True)
    amount_total  = fields.Float(related='ticket_id.amount_total', string="Total", readonly=True)
    partner_id    = fields.Many2one("res.partner", related='ticket_id.partner_id', string="Partner", readonly=True)
    invoice_2_general_public = fields.Boolean('General Public')
        

class AccountInvoiceLine(models.Model):
    _name = 'account.invoice.line'
    _inherit ='account.invoice.line'

    noidentificacion = fields.Char('NoIdentificacion', size=128)

    @api.multi
    def update_properties_concept(self, concepto):
        res = super(AccountInvoiceLine, self).update_properties_concept(concepto)
        for rec in self:
            if rec.noidentificacion:
                res.update({'NoIdentificacion':rec.noidentificacion})
        return res
