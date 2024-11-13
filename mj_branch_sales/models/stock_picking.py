

from odoo import models, fields, api

class StockPikcing(models.Model):
    _inherit = 'stock.picking'
    
    @api.model
    def create(self, vals):
        has_delivery=False
        picking = super(StockPikcing, self).create(vals)
        if picking and picking.origin and picking.carrier_id and picking.carrier_id.branch_id and picking.carrier_id.delivery_type=='onsite':
            sale_order=self.env['sale.order'].search([('name','=',picking.origin)])
            if sale_order:
                sale_order.write({'branch_id':picking.carrier_id.branch_id.id})
        return picking