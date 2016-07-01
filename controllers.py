# -*- coding: utf-8 -*-
from openerp.http import Controller, route, request

# class Openacademy(http.Controller):
#     @http.route('/openacademy/openacademy/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/openacademy/openacademy/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('openacademy.listing', {
#             'root': '/openacademy/openacademy',
#             'objects': http.request.env['openacademy.openacademy'].search([]),
#         })

#     @http.route('/openacademy/openacademy/objects/<model("openacademy.openacademy"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('openacademy.object', {
#             'object': obj
#         })

class Tcontr(Controller):

    @route("/hello/", auth='public', website=True)
    def index(self, **kw):
        period = request.env['hoc.period']
        return request.render('hoc_rent.index', {
                        'period': period.search([])
                                })
    
    @route("/Rental/", auth='public', website=True)
    def rent_show(self, **kw):
        return request.render("hoc_rent.web_hoc_rental", {})
