# -*- coding: utf-8 -*-
from odoo import http

# class HospitalAgreements(http.Controller):
#     @http.route('/hospital_agreements/hospital_agreements/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hospital_agreements/hospital_agreements/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hospital_agreements.listing', {
#             'root': '/hospital_agreements/hospital_agreements',
#             'objects': http.request.env['hospital_agreements.hospital_agreements'].search([]),
#         })

#     @http.route('/hospital_agreements/hospital_agreements/objects/<model("hospital_agreements.hospital_agreements"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hospital_agreements.object', {
#             'object': obj
#         })