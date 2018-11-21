# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class SouqOrder(models.Model):
    _name = 'souq.order'
    _inherit = 'mail.thread'
    name = fields.Char("Name", compute="_get_name", store="True")
    order_lines = fields.One2many(
        string=u'Order Lines',
        comodel_name='souq.order.line',
        inverse_name='order_id',
    )

    order_pic = fields.Binary("Image" , attachment=True)

    user_id = fields.Many2one('res.users', "Seller", default=lambda self: self.env.user)

    payment_method = fields.Selection(
        string='Payment Method',
        selection=[('cash', 'Cash'), ('bank', 'Bank')])

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
    total_price = fields.Float("Total Price", compute="_get_the_total_price", store="True")
    total_profit = fields.Float("Total Profit", compute="_get_the_total_profit", store="True")
    bookings = fields.One2many('souq.booking','order_id')
    num_booking = fields.Integer("Total Bookings", compute="get_the_number_of_bookings")
    # price_total = fields.Float('Total Price', readonly= True, )
    orders = fields.One2many('souq.order.line','order_id')
   

    @api.one
    def _get_my_orders(self):
        orders=self.search[()]
        myorders = []
        for order in orders:
            if order.user_id == self.env.user.id:
                myorders.append(order)
        
        return myorders
     
         
    @api.one
    def _get_name(self):
        self.name = "SQR-00" + str(self.id)


    @api.multi
    @api.depends('order_lines')
    def _get_the_total_price(self): 
        print(self)   
        total = 0.00
        for i in self:
            for line in i.order_lines:
                total += line.unit_price * line.qty
            i.total_price = total


######################################################
###############
    @api.depends('order_lines')
    def _get_the_total_profit(self): 
        print(self)
        sold_orders = self.env['souq.order'].search([('state','=','sold')])   
        total = 0.00
        for i in sold_orders:
            for line in i.order_lines:
                total += line.unit_price * line.qty
            i.total_profit = total
###############################################



    @api.onchange('bookings')
    def get_the_number_of_bookings(self):
    	t = 0
    	n_bookings = self.env['souq.booking'].search([])
    	for b in n_bookings:
    		if b.order_id.id == self.id:
    			t +=1
    	self.num_booking = t
    	return t
        
    def publish_order(self):
        self.state = 'available'

    def cancel_order(self):
        self.state = 'canceled'


    def view_order_bookings(self):
        
        context = {'order_id': self.id, },
        # view_id = self.ref('souq.')
        return {
            'name': 'Order Bookings',
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'list,form',
            'res_model': 'souq.booking',
            'domain': [('order_id', '=', self.id)],
            'context': context,
            'target': 'new',
        }
        


    # def view_followed_orders(self):
    #     myorders = self.env['souq.order'].search([('id', 'in', [x.res_id for x in self.env['mail.followers'].search([
    #         ('res_model', '=', 'souq.order'),
    #         ('partner_id', '=', self.env.user.partner_id.id),
    #         ])])])
    #     return myorders.ids

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


class OrderBooking(models.Model):
    
    _name = 'souq.booking'
    name = fields.Char("Name", compute="_get_name")
    order_id = fields.Many2one('souq.order', "Order")
    delivery_status = fields.Boolean('Delivery Status', related="order_id.delivery")
    requester_id = fields.Many2one('res.users', "Requester", default=lambda self: self.env.user)
    state = fields.Selection([('draft', 'Draft'), ('submitted', "Submitted"), ('accepted', "Accepted"), ('rejected', "Rejected"), ('confirmed', "Confirmed")], default='draft')
    date = fields.Datetime("Date", default=fields.Datetime.now)
    notes = fields.Text("Notes")
    requester_location = fields.Char("Requester Location")

    @api.one
    def _get_name(self):
        self.name = "ORB-00" + str(self.id)

    def submit_booking(self):
        self.state = 'submitted'

    def accept_booking(self):
        if self.order_id.state == 'available':
            self.order_id.state = 'booked'
            self.state = 'accepted'
        else:
            raise UserError("This order is already booked to another user")
            

    def reject_booking(self):
        if self.state=='accepted':
            self.order_id.state = 'available'
        self.state = 'rejected'

    def confirm_booking(self):
        self.state = 'confirmed'
        self.order_id.state = 'sold'
        
        new_so = self.env['sale.order'].create({
            'partner_id':self.requester_id.partner_id.id,
            'date_order':fields.Datetime.now(),
            'souq_order_id':self.order_id.id,
        })
        for line in self.order_id.order_lines:
            self.env['sale.order.line'].create({
                'product_id':line.product_id.id,
                'product_uom_qty':float(line.qty),
                'price_unit':line.unit_price,
                'order_id':new_so.id,
            })

class SaleOrder(models.Model):
    
    _inherit = ['sale.order']
    souq_order_id = fields.Many2one('souq.order', "Reference")
    pickup_location = fields.Char("Pickup Location", help="City - Area - Street")
    requester_location = fields.Char("Requester Location")
    payment_method = fields.Selection(
        string='Payment Method',
        selection=[('cash', 'Cash'), ('bank', 'Bank')]
    )

    delivery = fields.Boolean("Delivery?")



class PivotReport(models.Model):
    _inherit='souq.order'
    """docstring for PivotReport"""
    order_id = fields.Many2one('souq.order', "Order")
    # no_of_orders = fields.Integer( "no.orders",compute="_get_the_number_of_orders", store=True)
    # total_profit =
    # no.bookings =
    # sold =


    # @api.one
    # def get_the_number_of_orders(self):
    #     return True


    # @api.onchange('order_lines')
    # def _get_the_number_of_orders(self):

    #     orders = self.env['souq.order'].search([])
    #     # slod_orders = self.env['souq.order'].search([('state','=','sold')])
    #     count = 0
    #     for order in orders:
    #         for line in order.order_lines:
    #             count += 1
    #     self.no_of_orders = count
        

        
        # total = 0
        # for line in self.order_lines:
        #     total += 1
        # self.no_of_orders = total

    # @api.onchange('orders')
    # def get_the_number_of_orders(self):
    #     t = 0
    #     n_orders = self.env['souq.order'].search([])
    #     for b in n_orders:
    #         if b.order_id.id == self.id:
    #             t +=1
    #     self.no_orders = t
    #     return t


    # print()
    # print()
    # print()
    # print()        
    # print('self.no_of_orders')
    # print()
    # print()
    # print()    

# class Partner(models.Model):
#     _inherit = ['res.partner']
#     related_user_id = fields.Many2one('res.users', compute="_get_user_id", store=1)

#     def _get_user_id(self):
#         self.related_user_id = self.env['res.users'].search([
#             ('partner_id', '=', self.id)
#         ])


class Partner(models.Model):
    _inherit = ['res.partner']
    related_user_id = fields.Many2one('res.partner', default=lambda self: self.env.user.partner_id)
    cc = fields.Boolean(
        string=u'cc',
        default=lambda self: self._get_cc
    )
    
    def _get_user_id(self):
        self.related_user_id = self.env['res.users'].search([
            ('partner_id', '=', self.id)
        ])
    @api.one
    def _get_cc(self):
        if self.id == self.related_user_id:
            self.cc = True

# class User(models.Model):
    
#     _inherit = ['res.users']

#     @api.onchange('partner_id')
#     def check_user_partner_relation(self):
#         if self.partner_id:
#             self.partner_id.related_user_id = self.id
    