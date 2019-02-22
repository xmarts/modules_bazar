# -*- encoding: utf-8 -*-

from openerp import api, fields, models, _, tools
from openerp.exceptions import UserError


class res_partner(models.Model):
    _inherit = 'res.partner'

    use_partner_general = fields.Boolean(string='Usar para Publico en General', default=False)

    @api.multi
    @api.constrains('use_partner_general')
    def _check_use_partner_general(self):
        for record in self:
            if record.use_partner_general:
                res = self.search([('use_partner_general', '=', True)])
                if len(res) > 1:
                    raise UserError(
                        _("Error ! Solamente puedes tener un cliente seleccionado como cliente general con IVA."))
        return True

