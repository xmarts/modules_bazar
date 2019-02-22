from openerp import fields,models,api

class plantillas_wni_invoice(models.Model):

    _inherit = 'account.invoice.line'

    serie= fields.Text('No Serie', compute='_get_serie')

    @api.one
    @api.depends('serie', 'origin', 'product_id')
    def _get_serie(self):
        cr = self.env.cr
        if self.origin:
            sql = "select splot.name from stock_picking pi left join stock_move sp on sp.picking_id =pi.id  left join stock_move_line spl on spl.move_id=sp.id left join stock_production_lot splot on splot.id=spl.lot_id where  pi.origin='"+str(self.origin)+"' AND sp.product_id="+str(self.product_id.id)+" AND splot.name != 'None' AND spl.ordered_qty=spl.qty_done AND qty_done>0"
        else:
            ori = str(self.name)
            if(ori.find("Venta del ticket:")>=0):
                ori = ori.replace("Venta del ticket: ", "")
            else:
                ori = str(self.invoice_id.origin)
            if ori != '':
                sql = "select splot.name from stock_picking pi left join stock_move sp on sp.picking_id =pi.id	left join stock_move_line spl on spl.move_id=sp.id left join stock_production_lot splot on splot.id=spl.lot_id where  pi.origin='"+str(ori)+"' AND sp.product_id="+str(self.product_id.id)+" AND splot.name != 'None' AND spl.ordered_qty=spl.qty_done AND qty_done>0"
        cr.execute(sql)
        nseries = cr.fetchall()
        serie_text = ''
        cont1 = 0
        for t in nseries:
            if cont1 > 0:
                serie_text = serie_text + ", "
            serie_text = serie_text + str(t[0])
            cont1 = cont1 + 1
        self.serie = serie_text

