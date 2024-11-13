# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SalesBranch(models.Model):
    _name = 'mj.branch'
    _description = 'mj.branch'
    name = fields.Char()
    _sql_constraints = [
        ('unique_name','unique(name)','Name must be unique!'),
    ]
    @api.model
    def create(self, vals):
        branch = super(SalesBranch, self).create(vals)
        self.env['ir.ui.view'].create({
            'name': f"sale.order.branch.filter.{branch.name}",
            'model': 'sale.order',
            'inherit_id': self.env.ref('sale.view_sales_order_filter').id,
            'arch': f"""
                <xpath expr="//filter[@name='my_sale_orders_filter']" position="after">
                    <filter string="{branch.name}" name="branch_{branch.id}_filter" domain="[('branch_id', '=', '{branch.name}')]"/>
                </xpath>
            """
        })
        return branch
