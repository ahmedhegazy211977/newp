# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    branch_id = fields.Many2one('mj.branch', string='Branch')