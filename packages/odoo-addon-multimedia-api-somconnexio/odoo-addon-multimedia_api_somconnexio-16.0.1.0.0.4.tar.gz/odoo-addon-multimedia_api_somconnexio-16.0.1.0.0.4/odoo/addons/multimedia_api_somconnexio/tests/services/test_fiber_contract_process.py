from mock import patch

from odoo.addons.contract_api_somconnexio.tests.services.contract_process.base_test_contract_process import (  # noqa E501
    BaseContractProcessTestCase,
)
from odoo.addons.multimedia_somconnexio.models.crm_lead_line import CRMLeadLine
from odoo.addons.multimedia_somconnexio.tests.helper_service import crm_lead_create
from odoo.addons.multimedia_somconnexio.tests.utilities import (
    gen_multimedia_streaming_product,
)


class TestFiberContractProcess(BaseContractProcessTestCase):
    def setUp(self):
        super().setUp()
        self.FiberContractProcess = self.env["fiber.contract.process"]
        self.data = {
            "partner_id": self.partner.ref,
            "email": self.partner.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "Vodafone",
            "vodafone_fiber_contract_service_info": {
                "phone_number": "654123456",
                "vodafone_offer_code": "offer",
                "vodafone_id": "123",
            },
            "fiber_signal_type": "NEBAFTTH",
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.Fibra100Mb").default_code
                    ),
                    "date_start": "2020-01-01 00:00:00",
                }
            ],
            "iban": self.iban,
        }
        self.fiber_crm_lead = crm_lead_create(
            self.env,
            self.partner,
            "fiber",
            portability=False,
        )
        self.multimedia_product = gen_multimedia_streaming_product(self.env)

    @patch(
        "odoo.addons.contract_api_somconnexio.services.contract_process.fiber.FiberContractProcess._get_related_crm_lead_line"  # noqa E501
    )
    @patch.object(CRMLeadLine, "create_multimedia_contract")
    def test_create_fiber_in_lead_with_multimedia(
        self, mock_create_multimedia_contract, mock_get_related_crm_lead_line
    ):
        multimedia_line = self.env["crm.lead.line"].create(
            {
                "name": "Multimedia Service Line",
                "product_id": self.multimedia_product.id,
                "lead_id": self.fiber_crm_lead.id,
                "iban": self.iban,
            }
        )
        self.fiber_crm_lead.lead_line_ids |= multimedia_line

        mock_get_related_crm_lead_line.return_value = (
            self.fiber_crm_lead.lead_line_ids.filtered(lambda line: line.is_fiber)
        )
        content = self.FiberContractProcess.create(**self.data)

        mock_get_related_crm_lead_line.assert_called_with(content)
        mock_create_multimedia_contract.assert_called_once_with()

    @patch(
        "odoo.addons.contract_api_somconnexio.services.contract_process.fiber.FiberContractProcess._get_related_crm_lead_line"  # noqa E501
    )
    @patch.object(CRMLeadLine, "create_multimedia_contract")
    def test_create_fiber_in_lead_without_multimedia(
        self, mock_create_multimedia_contract, mock_get_related_crm_lead_line
    ):
        """
        Check than if a fiber contract when its CRM lead had no multimedia service line,
        no multimedia create job is enqueued.
        """

        mock_get_related_crm_lead_line.return_value = (
            self.fiber_crm_lead.lead_line_ids.filtered(lambda line: line.is_fiber)
        )

        content = self.FiberContractProcess.create(**self.data)

        contract = self.env["contract.contract"].browse(content["id"])
        self.assertTrue(
            contract.is_fiber,
        )
        mock_get_related_crm_lead_line.assert_called_with(content)
        mock_create_multimedia_contract.assert_not_called()
