# -*- encoding: utf-8 -*-

from openerp import api, fields, models, _, tools
from openerp.exceptions import UserError



class product_uom(models.Model):
    _inherit = 'product.template'

    use_product_general = fields.Boolean(string='Usar para Publico en General con IVA',default=False)

    @api.multi
    @api.constrains('use_product_general')
    def _check_use_product_general(self):
        for record in self:
            if record.use_product_general:
                res = self.search([('use_product_general', '=', True)])
                if len(res) > 1:
                    raise UserError(
                        _("Error ! Solamente puedes tener un producto seleccionado como producto general con IVA."))
        return True

