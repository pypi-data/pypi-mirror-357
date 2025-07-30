from odoo.addons.component.core import Component


class ProductCatalog(Component):
    _inherit = "product_catalog.service"

    def _get_product_category(self, product):
        category = product.product_tmpl_id.categ_id
        if category == self.env.ref("multimedia_somconnexio.streaming_service"):
            return "streaming"
        return super()._get_product_category(product)
