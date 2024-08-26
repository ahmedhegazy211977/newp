# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields


class ResCountryState(models.Model):
    _inherit = 'res.country.state'
    show_on_website = fields.Boolean('Show on website')