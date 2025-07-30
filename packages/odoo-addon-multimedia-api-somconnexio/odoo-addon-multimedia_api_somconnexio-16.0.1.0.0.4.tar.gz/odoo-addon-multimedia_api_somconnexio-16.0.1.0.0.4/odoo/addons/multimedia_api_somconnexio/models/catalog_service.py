from odoo import models


class CatalogService(models.AbstractModel):
    _inherit = "catalog.service"

    def service_products(self, service_category=None):
        parent_service_products = super().service_products(service_category)
        multimedia_categ_id = self.env.ref(
            "multimedia_somconnexio.multimedia_service"
        ).id
        service_product_templates = self.env["product.template"].search(
            [
                ("categ_id", "child_of", [multimedia_categ_id]),
            ]
        )

        multimedia_products = self._search_service_products_by_templates(
            service_product_templates
        )
        return parent_service_products + multimedia_products
