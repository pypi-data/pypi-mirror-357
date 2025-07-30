from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.addons.multimedia_somconnexio.tests.utilities import (
    gen_multimedia_streaming_product,
)


class TestCatalogService(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.multimedia_child_product = gen_multimedia_streaming_product(self.env)
        self.fiber_product = self.browse_ref("somconnexio.Fibra600Mb")
        self.fiber_product.contract_as_new_service = True

    def test_service_products(self):
        """Test that the service products include multimedia products."""
        service_products = self.env["catalog.service"].service_products()
        self.assertIn(self.multimedia_child_product, service_products)
        self.assertIn(self.fiber_product, service_products)
