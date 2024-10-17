from odoo import fields, models,api,_
import requests
import json
from odoo.exceptions import ValidationError
import logging
class StockPicking(models.Model):
    _inherit = "stock.picking"
    is_for_you_delivery = fields.Boolean('Is it leajlak delivery')
    for_you_state = fields.Selection([
        ('new', 'New'),
        ('ride', 'Start Ride'),
        ('in_shop', 'Reached Shop'),
        ('picked', 'Order Pikced'),
        ('shipped','Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ], string='Leajlak Delivery Status',default="new")
    
    @api.model
    def create(self, vals):
        res= super(StockPicking, self).create(vals)
        res.add_for_you_delivery()
        return res
    def get_shop_id(self,token):
        shop_id=0
        url = "https://staging.4ulogistic.com/api/partner/shops"
        headers={
            'Accept': 'application/json',
            'Authorization':'Bearer '+token
            }
        response = requests.get(url, data={}, headers=headers, verify=True)
        print(response.text)
        return_data=json.loads(response.text)
        if return_data and "shop_id" in return_data[0]:
            shop_id=return_data[0]['shop_id']
        return shop_id
    def add_for_you_delivery(self):
        if self.carrier_id and self.carrier_id.is_for_you_delivery:
            delivery_token = self.env['ir.config_parameter'].sudo().get_param('leajlak_delivery.foryou_delivery_token')
            if delivery_token:
                shop_id=self.get_shop_id(delivery_token)
                if shop_id !=0:
                    url = "https://staging.4ulogistic.com/api/partner/orders"
                    order=self.env['sale.order'].sudo().search([('name','=',self.origin)],limit=1)
                    order_note = order.sudo().note if order.sudo().note else ''
                    parms ={
                        "id": order.name,
                        "shop_id": shop_id,
                        "delivery_details": {
                            "name": self.partner_id.name,
                            "phone": self.partner_id.phone,
                            "coordinate": {
                                "latitude": 0,
                                "longitude": 0
                            },
                            "address": self.partner_id.contact_address
                        },
                        "order": {
                            "payment_type": '',
                            "delivery_charge" : 0,
                            "total": order.amount_total,
                            "notes": order_note
                        }
                    }
                    parms = json.dumps(parms)
                    headers={
                            'Accept': 'application/json',
                            'Authorization':'Bearer '+delivery_token,
                            'Content-Type': 'application/json'
                        }
                    response = requests.post(url, data=parms, headers=headers, verify=True)
                    return_data=json.loads(response.text)

                    if return_data and "dsp_order_id" in return_data:
                        self.carrier_tracking_ref=return_data["dsp_order_id"]
                        self.is_for_you_delivery=True
                        # self.carrier_tracking_url
                    else:
                        raise ValidationError(return_data)
                else:
                    raise ValidationError(_('There is no shop id'))
            else:
                raise ValidationError(_('There is no valid token in leajlak token setting!'))