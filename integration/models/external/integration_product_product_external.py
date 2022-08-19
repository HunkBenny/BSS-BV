# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class IntegrationProductProductExternal(models.Model):
    _name = 'integration.product.product.external'
    _inherit = 'integration.external.mixin'
    _description = 'Integration Product Product External'

    external_product_template_id = fields.Many2one(
        comodel_name='integration.product.template.external',
        string='External Product Template',
        readonly=True,
        ondelete='cascade',
    )

    def import_stock_levels(self, qty, location):
        self.ensure_one()

        variant = self.env['integration.product.product.mapping'].to_odoo(
            integration=self.integration_id,
            code=self.code,
        )

        if variant.type != 'product' or variant.tracking != 'none':
            return

        StockQuant = self.env['stock.quant'].with_context(skip_inventory_export=True)

        # Set stock levels to zero
        inventory_locations = self.env['stock.location'].search([
            ('parent_path', 'like', location.parent_path + '%'),
            ('id', '!=', location.id)
        ])

        inventory_quants = StockQuant.search([
            ('location_id', 'in', inventory_locations.ids),
            ('product_id', '=', variant.id),
        ])

        inventory_quants.inventory_quantity = 0
        inventory_quants.action_apply_inventory()

        # Set new stock level
        inventory_quant = StockQuant.search([
            ('location_id', '=', location.id),
            ('product_id', '=', variant.id),
        ])

        if not inventory_quant:
            inventory_quant = StockQuant.create({
                'location_id': location.id,
                'product_id': variant.id,
            })

        inventory_quant.inventory_quantity = float(qty)
        inventory_quant.action_apply_inventory()

    @api.model
    def fix_unmapped(self, integration):
        # Map unmapped templates
        ProductMapping = self.env['integration.product.product.mapping']
        ProductExternal = self.env['integration.product.product.external']
        TemplateMapping = self.env['integration.product.template.mapping']
        TemplateExternal = self.env['integration.product.template.external']

        product_mappings = ProductMapping.search([
            ('integration_id', '=', integration.id),
            ('product_id', '!=', False),
        ])

        for product_mapping in product_mappings:
            template = product_mapping.product_id.product_tmpl_id

            template_mapping = TemplateMapping.search([
                ('integration_id', '=', integration.id),
                ('template_id', '=', template.id),
            ])

            if not template_mapping:
                template_code = product_mapping.external_product_id.code.split('-')[0]
                template_external = TemplateExternal.get_external_by_code(
                    integration,
                    template_code,
                    raise_error=False
                )

                if template_external:
                    TemplateMapping.create_or_update_mapping(
                        integration,
                        template,
                        template_external
                    )

        # Create external products (XXX-0) and map it
        template_mappings = TemplateMapping.search([
            ('integration_id', '=', integration.id),
            ('template_id', '!=', False),
        ])

        for template_mapping in template_mappings:
            template_external = template_mapping.external_template_id
            variant = template_mapping.template_id.product_variant_ids

            product_external = ProductExternal.search([
                ('integration_id', '=', integration.id),
                ('code', '=like', template_external.code + '-%'),
            ])

            if not product_external and len(variant) == 1:
                product_external = ProductExternal.create({
                    'integration_id': integration.id,
                    'code': template_external.code + '-0',
                    'name': template_external.name,
                    'external_reference': template_external.external_reference,
                })

                if product_external:
                    ProductMapping.create_or_update_mapping(integration, variant, product_external)

    def _post_import_external_one(self, adapter_external_record):
        """
        This method will receive individual variant record.
        And link external variant with external template.
        """
        template_code = adapter_external_record.get('ext_product_template_id')
        if not template_code:
            raise UserError(
                _('External Product Variant should have "ext_product_template_id" field')
            )

        external_template = self.env['integration.product.template.external'].search([
            ('code', '=', template_code),
            ('integration_id', '=', self.integration_id.id),
        ])

        if not external_template:
            raise UserError(
                _('No External Product Template found with code %s. '
                  'Maybe templates are not exported yet?') % template_code
            )

        assert len(external_template) == 1  # just to doublecheck, as it should never happen
        self.external_product_template_id = external_template.id
