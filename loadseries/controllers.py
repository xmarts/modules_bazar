# -*- coding: utf-8 -*-
from openerp import http

# class Loadseries(http.Controller):
#     @http.route('/loadseries/loadseries/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/loadseries/loadseries/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('loadseries.listing', {
#             'root': '/loadseries/loadseries',
#             'objects': http.request.env['loadseries.loadseries'].search([]),
#         })

#     @http.route('/loadseries/loadseries/objects/<model("loadseries.loadseries"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('loadseries.object', {
#             'object': obj
#         })