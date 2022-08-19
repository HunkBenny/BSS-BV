#  See LICENSE file for full copyright and licensing details.

import pytz

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from ..prestashop_api import PrestaShopApiClient


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class SaleIntegration(models.Model):
    _inherit = 'sale.integration'

    type_api = fields.Selection(
        selection_add=[('prestashop', 'PrestaShop')],
        ondelete={
            'prestashop': 'cascade',
        },
    )

    presta_last_receive_orders_datetime = fields.Char(
        compute='_compute_presta_last_receive_orders_datetime',
    )

    product_delivery_in_stock = fields.Many2one(
        string='In-stock Delivery Days field',
        comodel_name='ir.model.fields',
        help='Define here field name belonging to Product (only Float and '
             'Integer fields accepted) where integration will get '
             'In-stock Product Delivery Days for Prestashop field '
             'Delivery time of in-stock products.',
        domain='[("model_id.model", "=", "product.template"),'
               ' ("ttype", "in", ("float", "integer")) ]',
    )

    message_templame_in_stock = fields.Char(
        string='Message Template For In-stock',
        translate=True,
        default='Delivery in {} days',
    )

    product_delivery_out_of_stock = fields.Many2one(
        string='Out-of-stock Delivery Days field',
        comodel_name='ir.model.fields',
        help='Define here field name belonging to Product (only Float and '
             'Integer fields accepted) where integration will get '
             'Out-of-stock Product Delivery Days for Prestashop field '
             'Delivery time of out-of-stock products with allowed orders.',
        domain='[("model_id.model", "=", "product.template"),'
               ' ("ttype", "in", ("float", "integer")) ]',
    )

    message_templame_out_of_stock = fields.Char(
        string='Message Template For Out-of-stock',
        translate=True,
        default='Delivery in {} days',
    )

    @api.depends('last_receive_orders_datetime')
    def _compute_presta_last_receive_orders_datetime(self):
        for integration in self:
            value = ''

            if integration.type_api == 'prestashop':
                ps_timezone = integration.get_settings_value('PS_TIMEZONE')
                if ps_timezone:
                    timezone = pytz.timezone(ps_timezone)
                    value = integration.last_receive_orders_datetime.astimezone(
                        timezone,
                    )
                    value = value.strftime(DATETIME_FORMAT)

            integration.presta_last_receive_orders_datetime = value

    def is_prestashop(self):
        self.ensure_one()
        return self.type_api == 'prestashop'

    def get_class(self):
        self.ensure_one()
        if self.is_prestashop():
            return PrestaShopApiClient

        return super().get_class()

    def action_active(self):
        self.ensure_one()
        result = super().action_active()

        if self.is_prestashop():
            adapter = self._build_adapter()
            ps_configuration = adapter._client.model('configuration')
            ps_timezone = ps_configuration.search({'name': 'PS_TIMEZONE'})[0].value
            self.set_settings_value('PS_TIMEZONE', ps_timezone)

        return result

    def convert_external_tax_to_odoo(self, tax_id):
        if not self.is_prestashop():
            return super(SaleIntegration, self).convert_external_tax_to_odoo(tax_id)

        assert_message = 'Prestashop integration expected product `taxes_id` as a string.'
        assert isinstance(tax_id, str) is True, assert_message

        external_tax_group = self.env['integration.account.tax.group.external'].search([
            ('integration_id', '=', self.id),
            ('code', '=', tax_id),
        ], limit=1)

        external_tax = external_tax_group.default_external_tax_id

        if not external_tax:
            tax_name = external_tax_group.name or tax_id

            raise ValidationError(_(
                'It is not possible to import product into Odoo, because you haven\'t defined '
                'default External Tax for Tax Group "%s". Please,  click "Quick Configuration" '
                'button on your integration "%s" to define that mapping.'
            ) % (tax_name, self.name))

        odoo_tax = self.env['account.tax'].from_external(
            self,
            external_tax.code,
        )

        return odoo_tax
