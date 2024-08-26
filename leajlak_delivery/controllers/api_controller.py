# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request,Response
import json
from odoo import exceptions
import random
import string
import base64
Status = {
"Order Accept":'new',
"Start Ride":'ride',
"Reached Shop":'in_shop',
"Order Picked":'picked',
"Shipped":'shipped',
"Delivered":'delivered',
"Canceled":'cancelled'
}



class APIConncetCompany(http.Controller):

    @http.route('/api/picking', auth='public', methods=['POST'],type='http', csrf=False)
    def update_delivert_state(self, **kw):
        try:
            data = json.loads(request.httprequest.data)
            if "id" in data and "status" in data:
                id=data['id']
                status=data['status']
                if status in Status:
                    real_state=Status[status]
                    sale_order= request.env['sale.order'].sudo().search([('name','=', id)])
                    picking=False
                    if sale_order:
                        if sale_order.picking_ids:
                            picking=sale_order.picking_ids[0]
                            if picking:
                                picking.write({
                                    'for_you_state':real_state
                                })
                        
                        if real_state =='delivered':
                            if sale_order.state !='sale':
                                sale_order.action_confirm()
                            if picking:
                                for l in picking.move_ids_without_package:
                                    l.write({"quantity":l.product_uom_qty})
                                picking.button_validate()
                        elif real_state =='cancelled':
                            if picking:
                                if picking.state=='done':
                                    tm=request.env['stock.return.picking'].sudo().new({
                                        'picking_id':picking.id
                                    })
                                    tm.sudo()._compute_moves_locations()
                                    tm.sudo()._create_returns()
                                elif picking.state !='cancel':
                                    picking.sudo().action_cancel()
                            #Cancel Order
                            if sale_order.state !='cancel':
                                sale_order.sudo()._action_cancel()

                        response_data = {
                            "status": 200,  
                            "message": "Status updated successfuly.",
                        }
                        json_response = json.dumps(response_data)
                        return json_response
                    else:
                        error="There is no sale order with this id"
                        json_response = json.dumps(response_data)
                        return json_response
                else:
                    response_data = {
                            "status": 200,  
                            "message": "There is no state '"+status+"' .",
                    }
                    json_response = json.dumps(response_data)
                    return json_response

            else:
                if "id" not in data:
                    error="There is no id in recieved data."
                if "status" not in data:
                    error="There is no id in recieved data."
                response_data = {
                    "status": 200,
                    "message": error,
                }
                json_response = json.dumps(response_data)
                return json_response
        except json.JSONDecodeError as e:
            response_data = {
                    "status": 400,
                    "message": "Invalid JSON data",
                }
            json_response = json.dumps(response_data)
            return json_response
        except Exception as e:
            response_data = {
                    "status": 500,
                    "message": "Error: " + str(e),
                }
            json_response = json.dumps(response_data)
            return json_response