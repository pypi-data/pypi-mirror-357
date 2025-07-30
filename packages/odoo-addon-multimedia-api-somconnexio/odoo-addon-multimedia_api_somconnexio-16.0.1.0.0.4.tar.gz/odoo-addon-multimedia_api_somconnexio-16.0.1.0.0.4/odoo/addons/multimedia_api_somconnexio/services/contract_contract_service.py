from odoo.addons.component.core import Component
from odoo.exceptions import MissingError
from odoo import models


class ContractMultimediaService(Component):
    _inherit = "base.rest.service"
    _name = "contract.multimedia.service"
    _usage = "contract/multimedia"
    _collection = "sc.api.key.services"
    _description = """
        Service to get multimedia contracts
    """

    def search(self, **params):
        multimedia_technology_id = self.env.ref(
            "multimedia_somconnexio.service_technology_multimedia"
        ).id
        partner_ref = params.get("partner_ref")
        domain = [
            ("partner_id.ref", "=", partner_ref),
            ("service_technology_id", "=", multimedia_technology_id),
        ]
        contracts = self.env["contract.contract"].sudo().search(domain)

        if not contracts:
            raise MissingError(
                (
                    "No multimedia contracts with partner_ref: {} could be found".format(  # noqa
                        partner_ref
                    )
                )
            )

        result = {"contracts": [self._to_dict(contract) for contract in contracts]}
        return result

    def _to_dict(self, contract):
        contract_dict = contract._to_dict()
        contract_dict.update({"subscription_code": contract.subscription_code})
        return contract_dict

    def _validator_search(self):
        return {"partner_ref": {"type": "string", "required": True}}


class ContractServiceModel(models.Model):
    _inherit = "contract.service"

    def _get_search_domain(self, **params):
        domain, search_params = super()._get_search_domain(**params)
        multimedia_technology_id = self.env.ref(
            "multimedia_somconnexio.service_technology_multimedia"
        ).id
        domain += [("service_technology_id", "!=", multimedia_technology_id)]
        return domain, search_params
