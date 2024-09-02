# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
_logger = logging.getLogger(__name__)
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

    
class WebsiteSaleGeolocation(WebsiteSale):
    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        # Fetch the Google Maps API key
        params = request.env['ir.config_parameter'].sudo()
        google_maps_api_key = params.get_param('base_geolocalize.google_map_api_key')

        # Call the original method
        response = super(WebsiteSaleGeolocation, self).address(**kw)
        # Update the rendering values with the Google Maps API key
        if isinstance(response, http.Response):
            response.qcontext.update({'google_maps_api_key': google_maps_api_key})

        return response
    
    def values_postprocess(self, order, mode, values, errors, error_msg):
        # Add custom fields to the authorized fields
        authorized_fields = request.env['ir.model']._get('res.partner')._get_form_writable_fields()
        authorized_fields['partner_latitude']={}
        authorized_fields['partner_longitude']={}
        new_values = {}
        for k, v in values.items():
            # don't drop empty value, it could be a field to reset
            if k in authorized_fields and v is not None:
                new_values[k] = v
            else:  # DEBUG ONLY
                if k not in ('field_required', 'partner_id', 'callback', 'submitted'): # classic case
                    _logger.debug("website_sale postprocess: %s value has been dropped (empty or not writable)" % k)

        if request.website.specific_user_account:
            new_values['website_id'] = request.website.id

        update_mode, address_mode = mode
        if update_mode == 'new':
            commercial_partner = order.partner_id.commercial_partner_id
            lang = request.lang.code if request.lang.code in request.website.mapped('language_ids.code') else None
            if lang:
                new_values['lang'] = lang
            new_values['company_id'] = request.website.company_id.id
            new_values['team_id'] = request.website.salesteam_id and request.website.salesteam_id.id
            new_values['user_id'] = request.website.salesperson_id.id

            if address_mode == 'billing':
                is_public_order = order._is_public_order()
                if is_public_order:
                    # New billing address of public customer will be their contact address.
                    new_values['type'] = 'contact'
                elif values.get('use_same'):
                    new_values['type'] = 'other'
                else:
                    new_values['type'] = 'invoice'

                # for public user avoid linking to default archived 'Public user' partner
                if commercial_partner.active:
                    new_values['parent_id'] = commercial_partner.id
            elif address_mode == 'shipping':
                new_values['type'] = 'delivery'
                new_values['parent_id'] = commercial_partner.id
        return new_values, errors, error_msg