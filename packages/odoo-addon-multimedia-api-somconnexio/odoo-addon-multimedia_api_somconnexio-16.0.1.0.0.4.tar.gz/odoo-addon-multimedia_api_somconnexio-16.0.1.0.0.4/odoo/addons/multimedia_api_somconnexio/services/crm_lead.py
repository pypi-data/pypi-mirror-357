from odoo.addons.component.core import Component


class CRMLeadService(Component):
    _inherit = "crm.lead.services"

    def _prepare_create_line(self, line, iban):
        multimedia_categ_id = self.env.ref(
            "multimedia_somconnexio.multimedia_service"
        ).id
        crm_line, product = self._prepare_create_crm_line(line, iban)
        if product.categ_id.parent_id.id == multimedia_categ_id:
            return crm_line
        return super()._prepare_create_line(line, iban)
