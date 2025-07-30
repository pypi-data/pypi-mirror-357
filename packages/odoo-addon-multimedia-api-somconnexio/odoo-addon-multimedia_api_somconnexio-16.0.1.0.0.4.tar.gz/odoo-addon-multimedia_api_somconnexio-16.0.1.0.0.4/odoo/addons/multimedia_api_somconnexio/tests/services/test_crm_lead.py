import json

from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin
from odoo.addons.multimedia_somconnexio.tests.utilities import (
    gen_multimedia_streaming_product,
)


class TestCRMLeadServiceRestCase(BaseRestCaseAdmin):
    def setUp(self):
        super().setUp()
        partner = self.env.ref("somconnexio.res_partner_1_demo")
        self.multimedia_streaming_product = gen_multimedia_streaming_product(self.env)
        self.multimedia_data = {
            "partner_id": partner.ref,
            "iban": "ES6621000418401234567891",
            "phone": "700284835",
            "lead_line_ids": [
                {
                    "product_code": (self.multimedia_streaming_product.default_code),
                }
            ],
        }
        self.url = "/api/crm-lead"

    def test_route_right_create_multimedia(self):
        response = self.http_post(self.url, data=self.multimedia_data)
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        (crm_lead,) = self.env["crm.lead"].browse(content["id"])
        crm_lead_line = crm_lead.lead_line_ids[0]
        self.assertEqual(
            self.multimedia_streaming_product.id, crm_lead_line.product_id.id
        )
