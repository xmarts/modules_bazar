# -*- coding: utf-8 -*-
import datetime
from openerp import models, fields, api, _, tools
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import xlrd
import shutil
import logging
import openerp
_logger = logging.getLogger(__name__)

class stockpickingloadseries(models.Model):
    _inherit = 'stock.picking'
    
    @api.one
    def update_series(self):

        attachment_obj = self.env['ir.attachment']
        attachments = []
        company_id = self.company_id.id
        stockpicking = self
        #fname_stockpicking = stockpicking.fname_stockpicking and stockpicking.fname_stockpicking or ''
        adjuntos = attachment_obj.search([('res_model', '=', 'stock.picking'), 
                                              ('res_id', '=', stockpicking.id)])
        #raise UserError(_("Error:Hay \n%s!") % (stockpicking.id))
        _logger.error(" archivos ajuntos" )
        ruta= "/var/lib/odoo/filestore/"
        count = 0
        for attach in adjuntos:                
          count += 1

        if count >= 2 or count == 0:
          raise UserError(_("Error:Hay \n%s archivos adjuntos, por favor adjunte el archivo o sólo deje el archivo para cargar sus series!") % (count))
        else:
          if count == 1:
            db_name = self._cr.dbname
            _logger.error("hay 1 archivo ajuntos")
            destino = ruta +db_name +"/" + adjuntos.store_fname+".xls";
            #destino = "/var/lib/odoo/.local/share/Odoo/filestore/fortuna/" + adjuntos.store_fname+".xls";
            #shutil.copy('/var/lib/odoo/.local/share/Odoo/filestore/fortuna/' + adjuntos.store_fname, destino)
            shutil.copy(ruta+db_name +'/'  + adjuntos.store_fname, destino)
            _logger.info("ARCHIVO COPIADO")
            #book = xlrd.open_workbook("/var/lib/odoo/.local/share/Odoo/filestore/fortuna/" + adjuntos.store_fname+".xls")
            book = xlrd.open_workbook(ruta+db_name +"/"  + adjuntos.store_fname+".xls")
            #serie_obj = self.pool.get('serie_tmp')
            sheet = book.sheet_by_index(0)

            nrows = sheet.nrows
            ncols = sheet.ncols
            _logger.info( nrows)
            _logger.info( ncols)
            for i in range(nrows):
                for j in range(ncols):
                    #string += '%st'%sheet.cell_value(i,j)
                    _logger.info(sheet.cell_value(i,0) )
                    _logger.info(sheet.cell_value(i,1) )
                    #if sheet.cell_value(i,4) == '':
                    #   raise UserError(_("Error:vacio columna 5 \n%s!") % ())
                    serie_obj = self.env['series_tmp']
                    self.write({'xls_file_signed_index' : adjuntos.store_fname})
                    serie_vals = {
                      'producto': sheet.cell_value(i,0),
                      'serie': sheet.cell_value(i,1),
                      'stockpicking_id': stockpicking.id,
                    }
                serie_create_id = serie_obj.create(serie_vals)
                _logger.info("Termino de guardar")
    @api.one
    def loads_series(self):
        adjuntos = self.env['ir.attachment'].search([('res_model', '=', 'stock.picking'),
                                              ('res_id', '=', self.id)])
        ruta ="/var/lib/odoo/filestore/"

        if len(adjuntos) != 1:
          raise UserError(_("Error:Hay \n%s archivos adjuntos, por favor adjunte el archivo o sólo deje el archivo para cargar sus series!") % (len(adjuntos)))
        else:
            db_name = self._cr.dbname
            destino = ruta+db_name +"/"  + adjuntos.store_fname;
            #shutil.copy(ruta+db_name +"/"  + adjuntos.store_fname, destino)
            #_logger.info("ARCHIVO COPIADO")
            book = xlrd.open_workbook(destino)
            sheet = book.sheet_by_index(0)

            nrows = sheet.nrows #Numero filas
            ncols = sheet.ncols #Numero columnas
            _logger.info( nrows)
            _logger.info( ncols)
            apagador = False
            if ncols != 2:
                raise UserError(_(
                    "Error\n La estructura del XLS esta mal ya que no cuenta con las columnas necesiaras para la importacion (nombre del producto, No. de serie/ Lote)!"))
            for i in range(nrows):
                _logger.info(sheet.cell_value(i,0) )
                _logger.info(sheet.cell_value(i,1) )
                nombre = str(sheet.cell_value(i,0))
                serie = sheet.cell_value(i,1)
                for product_lines in self.move_lines:
                    if nombre.replace('.0','') in product_lines.product_id.code or nombre in product_lines.product_id.name:
                        if len(product_lines.move_line_ids) == 1:
                            product_lines.move_line_ids.lot_name = str(serie).replace(".0","")
                            product_lines.move_line_ids.qty_done = product_lines.move_line_ids.product_uom_qty
                            apagador = True
                        elif len(product_lines.move_line_ids) == 0:
                            product_lines.move_line_ids.create({
                                'picking_id' : self.id,
                                'move_id' : product_lines.id,
                                'product_id' : product_lines.product_id.id,
                                'product_uom_id' : product_lines.product_id.uom_id.id,
                                'product_uom_qty' : 1.000,
                                'ordered_qty' : 1.000,
                                'qty_done' : 1.000,
                                'lot_name' : str(serie).replace(".0",""),
                                'date' : datetime.datetime.now(),
                                'location_id' : product_lines.location_id.id,
                                'location_dest_id' : product_lines.location_dest_id.id
                            })
                            apagador = True
                        else:
                            apagador = True
                            for line in product_lines.move_line_ids:
                                if not line.lot_name:
                                    line.lot_name = str(serie).replace(".0","")
                                    line.qty_done = line.product_uom_qty
                                    break
                                else:
                                    if line.lot_name == str(serie).replace(".0",""):
                                        line.qty_done = line.product_uom_qty
                                        break
            if apagador == False:
                raise UserError(_(
                    "Error\n Ningun nombre del producto que viene en el excel fue encontrado, favor de mejor utilizar el codigo de producto y validar que sean identicos."))






    @api.one
    def series_aleatoria(self):
        for product_lines in self.move_lines:
            obj = self.env['stock.move.line'].search([('product_id','=',product_lines.product_id.id),('lot_name','ilike','AL')])
            if len(obj) == 0:
                serie = 'AL-1000001'
            else:
                tmp = None;
                if len(obj)==1:
                    tmp=int(obj.lot_name.replace('AL-',''))
                else:
                    for s in obj:
                        if not tmp:
                            tmp = int(s.lot_name.replace('AL-',''))
                        elif tmp < int(s.lot_name.replace('AL-','')):
                            tmp = int(s.lot_name.replace('AL-',''))
                serie_int= int(tmp)+ 1
                serie = 'AL-'+str(serie_int)
            if len(product_lines.move_line_ids) == 1:
                product_lines.move_line_ids.lot_name = str(serie)
                product_lines.move_line_ids.qty_done = product_lines.move_line_ids.product_uom_qty
            elif len(product_lines.move_line_ids) == 0:
                product_lines.move_line_ids.create({
                    'picking_id': self.id,
                    'move_id': product_lines.id,
                    'product_id': product_lines.product_id.id,
                    'product_uom_id': product_lines.product_id.uom_id.id,
                    'product_uom_qty': 1.000,
                    'ordered_qty': 1.000,
                    'qty_done': 1.000,
                    'lot_name': str(serie),
                    'date': datetime.datetime.now(),
                    'location_id': product_lines.location_id.id,
                    'location_dest_id': product_lines.location_dest_id.id
                })
            else:
                for line in product_lines.move_line_ids:
                    if not line.lot_name:
                        line.lot_name = str(serie)
                        line.qty_done = line.product_uom_qty
                        tmp = int(serie.replace('AL-', ''))
                        serie_int = int(tmp) + 1
                        serie = 'AL-' + str(serie_int)

