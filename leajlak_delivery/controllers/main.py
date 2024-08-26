# from odoo.http import content_disposition, Controller, request, route

# from odoo.addons.portal.controllers.portal import CustomerPortal
# from odoo.addons.website_sale.controllers.main import WebsiteSale

    
# class WebsiteSaleInherit(WebsiteSale):
#     def _checkout_form_save(self, mode, checkout, all_values):
#         Partner = request.env['res.partner']
#         if 'latitude' in all_values:
#             checkout['latitude']=all_values['latitude']
#         if 'longitude' in all_values:
#             checkout['longitude']=all_values['longitude']
#         if mode[0] == 'new':
#             partner_id= Partner.sudo().with_context(tracking_disable=True).create(checkout).id
#         elif mode[0] == 'edit':
#             partner_id = int(all_values.get('partner_id', 0))
#             if partner_id:
#                 # double check
#                 order = request.website.sale_get_order()
#                 shippings = Partner.sudo().search([("id", "child_of", order.partner_id.commercial_partner_id.ids)])
#                 if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
#                     return Forbidden()
#                 Partner.browse(partner_id).sudo().write(checkout)
#         return partner_id
#     def _get_mandatory_fields_shipping(self, country_id=False):
#         req = ["name", "street", "city", "country_id", "phone","latitude","longitude"]
#         if country_id:
#             country = request.env['res.country'].browse(country_id)
#             if country.state_required:
#                 req += ['state_id']
#             if country.zip_required:
#                 req += ['zip']
#         return req