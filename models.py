# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions
import logging

_logger = logging.getLogger(__name__)

class GroupProducts(models.Model):
    
    _name = 'hoc.nbr_products'

    name = fields.Char(string='Name', compute='_compute_name')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Integer()
    reservation_id = fields.Many2one(
        'hoc.reservation',
        compute='_compute_parent_reservation',
        ondelete='cascade'
        )
    price = fields.Float(digit=(6,2), compute='_compute_price')

    @api.one
    def _compute_parent_reservation(self):
        cr = self._cr
        uid = self._uid
        reservations = self.pool.get('hoc.reservation')
        res_id = reservations.search(cr, uid, [('group_product_ids','=',self.id)])
        self.reservation_id = reservations.browse(cr, uid, res_id)
        print "updated field reservation_id:", self.reservation_id

    @api.depends('product_id','quantity')
    def _compute_name(self):
        for record in self:
            record.name = unicode(record.product_id.name) + u'_x' + unicode(record.quantity)

    @api.depends('product_id','quantity')
    def _compute_price(self):
        for rec in self:
            price = rec.product_id.rental_price_by_day * rec.quantity
            if rec.quantity >= rec.product_id.rental_discount_offset:
                price = price - (price * rec.product_id.rental_discount_amount / 100)
            rec.price = price

class Reservation(models.Model):

    _name = 'hoc.reservation'

    #name = fields.Char(compute = '_compute_name')
    description = fields.Text()
    start_date = fields.Date()
    end_date = fields.Date()
    group_product_ids = fields.Many2many('hoc.nbr_products', string="Product")
    product_ids = fields.Many2many('product.product', compute='_compute_related_products')
    user_id = fields.Many2one(
        'res.users',
        string = "Rental user",
        default = lambda self: self._default_user()
        )
    reservation_type = fields.Selection(
        [('event','Event'), ('rental','Rental')],
        default='rental'
        )
    days = fields.Integer(compute='_compute_days')
    price = fields.Float(digit=(6,2), compute='_compute_price')
    
    def _default_user(self):
        return self.env.user
    
    #TODO issue : this is computed 2 times : at group_products creation and at the reservation creation 
    @api.depends('group_product_ids','product_ids')
    def _compute_related_products(self):
        for group in self.group_product_ids:
            print "group.product_id", group.product_id
            self.product_ids += group.product_id
    """
    @api.depends('group_product_ids')
    def _compute_name(self):
        name = ""
        for rec in self:
            for group in rec.group_product_ids:
                name = name + group.product_id.name + '_'
        self.name = name
    """        
    @api.depends('start_date', 'end_date')
    def _compute_days(self):
        for rec in self:
            try:
                rec.days = (fields.Date.from_string(rec.end_date) - fields.Date.from_string(rec.start_date)).days
            except:
                rec.days = 0
    
    @api.depends('group_product_ids')
    def _compute_price(self):
        for rec in self:
            total_price = 0
            for group_product in rec.group_product_ids:
                group_price = group_product.price * rec.days
                total_price += group_price
            rec.price = total_price
    
    @api.constrains('start_date', 'end_date')
    def _check_start_end(self):
        for rec in self:
            if fields.Date.from_string(rec.start_date) >=\
                fields.Date.from_string(rec.end_date):
                raise exceptions.ValidationError("The start date must be before end date!")
            if fields.Date.from_string(rec.start_date) <=\
                fields.Date.from_string(fields.Date.today()):
                raise exceptions.ValidationError("The start date must be later than today!")
    
    @api.one
    @api.constrains('group_product_ids')
    def _check_conficted_periods(self):
        reservations = self.pool.get('hoc.reservation')
        for group_product in self.group_product_ids:
            if not group_product.product_id.rentable:
                raise exceptions.ValidationError(
                    group_product.product_id.name+\
                    " cannot be rent! You can change this setting in the product page."
                    )
            if group_product.product_id.qty_available == 0:
                raise exceptions.ValidationError("There is no product in stock")

            conflict_periods = []
            
            ids_of_concerned_reservations = reservations.search(
                self._cr,
                self._uid,
                [('id', '!=', self.id)
                ])

            for id_reservation in ids_of_concerned_reservations:
                reservation = reservations.browse(self._cr, self._uid, [id_reservation])

                r_start = fields.Date.from_string(reservation.start_date)
                r_end = fields.Date.from_string(reservation.end_date)
                intented_start = fields.Date.from_string(self.start_date)
                intented_end = fields.Date.from_string(self.end_date)

                if intented_end >= r_start and intented_end <= r_end:
                    conflict_periods.append(reservation)
                elif intented_start <= r_end and intented_start >= r_start:
                    conflict_periods.append(reservation)
                elif intented_start <= r_start and intented_end >= r_end:
                    conflict_periods.append(reservation)

            if len(conflict_periods) >= group_product.product_id.qty_available:
                raise exceptions.ValidationError(
                    "Not enough products for this period!\n conflict_periods:"\
                    +str(conflict_periods)+"\nFor:"\
                    +str(self)
                    )
            if group_product.product_id.qty_available < group_product.quantity:
                raise exceptions.ValidationError(
                    "Not enough "+group_product.product_id.name+ " !"
                    )
            
