from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_multimedia = fields.Boolean(
        string="Is Multimedia",
        compute="_compute_is_multimedia",
        default=False,
    )
    sale_subscription_template_id = fields.Many2one(
        comodel_name="sale.subscription.template",
        string="Subscription Template",
        help="Subscription template to use for this product.",
    )

    def _compute_is_multimedia(self):
        main_multimedia_service = self.env.ref(
            "multimedia_somconnexio.multimedia_service"
        )
        all_multimedia_categories = self.env["product.category"].search(
            [("id", "child_of", main_multimedia_service.id)]
        )
        for product in self:
            product_category = product.product_tmpl_id.categ_id
            if product_category:
                product.is_multimedia = product_category in all_multimedia_categories
            else:
                product.is_multimedia = False
