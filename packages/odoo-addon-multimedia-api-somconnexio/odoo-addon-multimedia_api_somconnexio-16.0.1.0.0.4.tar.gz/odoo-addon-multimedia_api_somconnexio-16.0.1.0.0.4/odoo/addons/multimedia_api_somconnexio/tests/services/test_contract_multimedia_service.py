import odoo
from mock import patch
import json
from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin
from odoo.addons.multimedia_somconnexio.tests.utilities import gen_multimedia_contract


class TestContractMultimediaController(BaseRestCaseAdmin):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.contract_multimedia = gen_multimedia_contract(self.env)
        self.partner = self.contract_multimedia.partner_id
        self.params = {"partner_ref": self.partner.ref}
        self.url = "/api/contract/multimedia"

    @patch("odoo.addons.contract_api_somconnexio.models.contract.Contract._to_dict")
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_multimedia_contracts_ok(self, mock_to_dict):
        mock_to_dict.return_value = {"id": self.contract_multimedia.id}

        response = self.http_get(self.url, params=self.params)
        self.assertEqual(response.status_code, 200)

        result = json.loads(response.content.decode("utf-8"))["contracts"]
        result_contract = next(
            contract
            for contract in result
            if contract["id"] == self.contract_multimedia.id
        )
        self.assertEqual(result_contract["id"], self.contract_multimedia.id)
        self.assertEqual(
            result_contract["subscription_code"],
            self.contract_multimedia.subscription_code,
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_multimedia_contracts_bad_request(self):
        response = self.http_get(self.url, params={"partner_nif": self.partner.ref})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.reason, "BAD REQUEST")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_multimedia_contracts_not_found(self):
        response = self.http_get(self.url, params={"partner_ref": "666"})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.reason, "NOT FOUND")
