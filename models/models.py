# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SouqOrder(models.Model):
    _name = 'souq.order'
    _inherit = 'mail.thread'
    name = fields.Char("Name", compute="_get_name")
    order_lines = fields.One2many(
        string=u'Order Lines',
        comodel_name='souq.order.line',
        inverse_name='order_id',
    )
    user_id = fields.Many2one('res.users', "Seller", default=lambda self: self.env.user)
    payment_method = fields.Selection(
        string='Payment Method',
        selection=[('cash', 'Cash'), ('bank', 'Bank')]
    )

    delivery = fields.Boolean("Delivery?")
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('available', 'Available'), ('booked', "Booked"), ('sold', "Sold"), ('canceled', "Canceled")],
        default='draft'
    )
    date = fields.Datetime("Order Date", default=fields.Datetime.now)
    phone = fields.Char("Phone", 
    related='user_id.phone',
    )
    pickup_location = fields.Char("Pickup Location", help="City - Area - Street")
    total_price = fields.Float("Total Price", compte="_get_the_total_price")
    
    @api.one
    def _get_name(self):
        self.name = "SQR-00" + str(self.id)

    @api.onchange('order_lines')
    def _get_the_total_price(self): 
        print(self)   
        total = 0.00
        for line in self.order_lines:
            total += line.unit_price * line.qty
        self.total_price = total

class SouqOrderLine(models.Model):
    _name = 'souq.order.line'
    order_id = fields.Many2one(
        comodel_name='souq.order',
        ondelete='set null',)
    product_id = fields.Many2one(
        comodel_name='product.template',
        ondelete='set null',)
    qty = fields.Integer()
    unit_price = fields.Float("Price")
    used_duration = fields.Integer("Used / Months")


    
    
    
    