# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    branch_id = fields.Many2one('mj.branch', string='Branch')