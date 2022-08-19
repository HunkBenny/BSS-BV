# See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models, api
from odoo.tools.float_utils import float_compare


_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'integration.model.mixin']

    integration_id = fields.Many2one(
        string='e-Commerce Integration',
        comodel_name='sale.integration',
        readonly=True
    )

    integration_delivery_note = fields.Text(
        string='e-Commerce Delivery Note',
        copy=False,
    )

    external_sales_order_ref = fields.Char(
        string='External Sales Order Ref',
        compute='_compute_external_sales_order_ref',
        readonly=True,
        store=True,
        help='This is the reference of the Sales Order in the e-Commerce System.',
    )

    related_input_files = fields.One2many(
        string='Related input files',
        comodel_name='sale.integration.input.file',
        inverse_name='order_id',
    )

    sub_status_id = fields.Many2one(
        string='e-Commerce Order Status',
        comodel_name='sale.order.sub.status',
        domain='[("integration_id", "=", integration_id)]',
        ondelete='set null',
        copy=False,
    )

    type_api = fields.Selection(
        string='Api service',
        related='integration_id.type_api',
        help='Technical field',
    )

    payment_method_id = fields.Many2one(
        string='e-Commerce Payment method',
        comodel_name='sale.order.payment.method',
        domain='[("integration_id", "=", integration_id)]',
        ondelete='set null',
        copy=False,
    )

    integration_amount_total = fields.Monetary(
        string='e-Commerce Total Amount',
    )

    is_total_amount_difference = fields.Boolean(
        compute='_compute_is_total_amount_difference'
    )

    def write(self, vals):
        statuses_before_write = {}

        if vals.get('sub_status_id'):
            for order in self:
                statuses_before_write[order] = order.sub_status_id

        result = super().write(vals)

        if vals.get('sub_status_id'):
            for order in self:
                if statuses_before_write[order] == order.sub_status_id:
                    continue

                integration = order.integration_id
                if not integration:
                    continue

                if not integration.job_enabled('export_sale_order_status'):
                    continue

                key = f'export_sale_order_status_{order.id}'
                integration.with_context(company_id=integration.company_id.id).with_delay(
                    identity_key=key
                ).export_sale_order_status(order)

        return result

    @api.depends('amount_total', 'integration_amount_total')
    def _compute_is_total_amount_difference(self):
        for order in self:
            if not order.integration_amount_total:
                order.is_total_amount_difference = False
            else:
                order.is_total_amount_difference = float_compare(
                    value1=order.integration_amount_total,
                    value2=order.amount_total,
                    precision_digits=self.env['decimal.precision'].precision_get('Product Price'),
                ) != 0

    @api.depends('related_input_files')
    def _compute_external_sales_order_ref(self):
        for order in self:
            reference_list = order.related_input_files.mapped('order_reference')
            order.external_sales_order_ref = ', '.join(reference_list) or ''

    def _cancel_order_hook(self):
        for order in self:
            if order.integration_id.run_action_on_cancel_so:
                method_name = '_%s_cancel_order' % order.integration_id.type_api
                if hasattr(order, method_name):
                    getattr(order, method_name)()
                else:
                    _logger.warning("No method found with name '%s'" % method_name)

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        if res is True:
            self._cancel_order_hook()
        return res
