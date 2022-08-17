# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ImportStockLevelsWizard(models.TransientModel):
    _name = "import.stock.levels.wizard"
    _description = "Import Stock Levels Wizard"

    location_id = fields.Many2one(
        string='Specify Location to import Stock',
        comodel_name='stock.location',
        domain=lambda self: [
            ('company_id', '=', self._get_company_id()),
            ('usage', '=', 'internal')
        ],
        required=True,
    )

    @api.model
    def _get_company_id(self):
        integration = self._get_sale_integration()
        return integration.company_id.id if integration else None

    @api.model
    def _get_sale_integration(self):
        integration = self.env['sale.integration'].browse(self._context.get('active_ids'))
        return integration[0] if integration else None

    def run_import(self):
        integration = self._get_sale_integration()
        adapter = integration._build_adapter()

        stock_levels = adapter.get_stock_levels()

        ProductProductExternal = self.env['integration.product.product.external']

        for variant_code, qty in stock_levels.items():
            variant_external = ProductProductExternal.get_external_by_code(
                integration,
                variant_code,
                raise_error=False
            )

            if variant_external:
                variant_external = variant_external.with_context(
                    company_id=integration.company_id.id
                )
                variant_external.with_delay(
                    description='Import Stock Levels'
                ).import_stock_levels(qty, self.location_id)
