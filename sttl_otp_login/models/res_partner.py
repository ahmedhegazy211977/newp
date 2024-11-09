from odoo import api, fields, models
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.model
    def create(self, vals):
        res= super(ResPartner, self).create(vals)
        related_otp=self.env['otp.verification'].search([('email', '=', vals['email'])], order="create_date desc", limit=1)
        if related_otp:
            res.mobile=related_otp.mobile
        return res