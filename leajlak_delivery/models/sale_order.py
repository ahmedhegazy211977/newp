from odoo import fields, models,api
import requests
import json
# Status = {
# "new":'جديد',
# "ride":'الكابتن في الطريق للمطعم',
# "in_shop":'الكابتن في المطعم',
# "picked":'تم اخذ الطب',
# "shipped":'تم الشحن',
# "delivered":'تم التوصيل',
# "cancelled":'تم الالغاء'
# }
class SaleOrder(models.Model):
    _inherit = "sale.order"
    leajlak_delivery_state = fields.Selection([
        ('new', 'New'),
        ('ride', 'Start Ride'),
        ('in_shop', 'Reached Shop'),
        ('picked', 'Order Pikced'),
        ('shipped','Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ],compute='_compute_leajlak_delivery_state', string='Leaklak Delivery State')
    @api.depends('picking_ids')
    def _compute_leajlak_delivery_state(self):
        for record in self:
            record.leajlak_delivery_state=""
            if record.picking_ids:
                for p in record.picking_ids:
                    if p.is_for_you_delivery:
                        record.leajlak_delivery_state=p.for_you_state