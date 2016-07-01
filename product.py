from openerp import fields, models, api, exceptions

class Product(models.Model):
    _inherit = 'product.product'

    rentable = fields.Boolean("Can be rent", default=False)
    rental_price_by_day = fields.Float(digits=(6,2))
    group_product_ids = fields.One2many('hoc.nbr_products', 'product_id',readOnly=True)
    reservation_ids = fields.Many2many('hoc.reservation', compute='_compute_related_reservations')
    rental_discount_offset = fields.Integer(
        "Discount offset",
        help="Necessary number of products to enable the discount"
        )
    rental_discount_amount = fields.Integer(
        "Discount amount",
        help="Discount amount, in percent",
        default=0
        )

    @api.depends('group_product_ids')
    def _compute_related_reservations(self):
        for group_product in self.group_product_ids:
            self.reservation_ids += group_product.reservation_id

    
