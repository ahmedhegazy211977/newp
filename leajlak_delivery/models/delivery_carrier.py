from odoo import fields, models


class DeliveryCarrier(models.Model):
   _inherit = "delivery.carrier"
   is_for_you_delivery = fields.Boolean('Leajlak Delivery')