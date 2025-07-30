import json
from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin
from odoo.addons.multimedia_somconnexio.tests.utilities import gen_multimedia_contract


class TestContractSearchController(BaseRestCaseAdmin):
    def setUp(self):
        super().setUp()
        self.url = "/api/contract"
        self.partner = self.browse_ref("somconnexio.res_partner_1_demo")
        self.mobile_contract = self.env.ref("somconnexio.contract_mobile_il_20")
        self.fiber_contract = self.env.ref("somconnexio.contract_fibra_600")
        self.multimedia_contract = gen_multimedia_contract(self.env)

    def test_route_contract_search_without_multimedia(self):
        url = "{}?{}={}&{}={}".format(
            self.url, "customer_ref", self.mobile_contract.partner_id.ref, "limit", 50
        )
        response = self.http_get(url)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content.decode("utf-8"))
        self.assertNotIn(
            self.multimedia_contract.id, [c["id"] for c in result["contracts"]]
        )
