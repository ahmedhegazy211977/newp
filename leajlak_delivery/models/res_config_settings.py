from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """ Inherited this module is to add fields for ForYou Delivery authentication """
    _inherit = "res.config.settings"
    foryou_delivery_token = fields.Char(string="Leajlak Auth Token",config_parameter='leajlak_delivery.foryou_delivery_token',help="For You Auth Token")