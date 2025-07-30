from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin
from odoo.addons.multimedia_somconnexio.tests.utilities import (
    gen_multimedia_streaming_product,
)
import json


class TestProductCatalogController(BaseRestCaseAdmin):
    def setUp(self):
        super().setUp()
        self.url = "/api/product-catalog"
        self.params = {"code": "21IVA"}
        self.multimedia_streaming_product = gen_multimedia_streaming_product(self.env)

    def test_get_product_category(self):
        """Test that the product category is correctly identified as."""
        response = self.http_get(self.url, params=self.params)
        content = json.loads(response.content.decode("utf-8"))
        obtained_pricelist = content.get("pricelists")[0].get("products")
        self.assertEqual(
            next(
                (
                    p
                    for p in obtained_pricelist
                    if p["code"] == "test_multimedia_product"
                ),
                None,
            )["category"],
            "streaming",
        )
