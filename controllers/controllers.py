# -*- coding: utf-8 -*-
from odoo import http

# class Souq(http.Controller):
#     @http.route('/souq/souq/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/souq/souq/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('souq.listing', {
#             'root': '/souq/souq',
#             'objects': http.request.env['souq.souq'].search([]),
#         })

#     @http.route('/souq/souq/objects/<model("souq.souq"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('souq.object', {
#             'object': obj
#         })