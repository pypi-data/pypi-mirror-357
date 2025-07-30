from odoo.models import AbstractModel


class FiberContractProcess(AbstractModel):
    _inherit = "fiber.contract.process"
    _description = """
        Fiber Contract creation
    """

    def create(self, **params):
        contract_dict = super().create(**params)
        self._activate_lead_multimedia_services(contract_dict)
        return contract_dict

    def _activate_lead_multimedia_services(self, contract_dict):
        """
        Activate multimedia services related to the fiber contract once created.
        """
        crm_lead_line = self._get_related_crm_lead_line(contract_dict)
        if not crm_lead_line:
            return True

        multimedia_lines = crm_lead_line.lead_id.lead_line_ids.filtered("is_multimedia")

        if not multimedia_lines:
            return True

        for line in multimedia_lines:
            line.with_delay().create_multimedia_contract()
