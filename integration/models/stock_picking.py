# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    tracking_exported = fields.Boolean(
        string='Is Tracking Exported?',
        default=False,
        help='This flag allows us to define if tracking code for this picking was exported '
             'for external integration. It helps to avoid sending same tracking number twice. '
             'Basically we need this flag, cause different carriers have different type of '
             'integration. And sometimes tracking reference is added to stock picking after it '
             'is validated and not at the same moment.',
    )

    def to_export_format(self, integration):
        self.ensure_one()

        lines = []
        for move_line in self.move_lines:
            sale_line = move_line.sale_line_id
            line = {
                'id': sale_line.to_external(integration),
                'qty': move_line.quantity_done,
            }
            lines.append(line)

        result = {
            'sale_order_id': self.sale_id.to_external(integration),
            'tracking': self.carrier_tracking_ref,
            'lines': lines,
        }

        if self.carrier_id:
            result['carrier'] = self.carrier_id.to_external(integration)

        return result

    def write(self, vals):
        res = super(StockPicking, self).write(vals)

        if res:
            done_pickings_with_tracking = (
                self
                # only send for Done pickings that were not exported yet
                # and if this is final Outgoing picking OR dropship picking
                .filtered(lambda x: x.state == 'done' and not x.tracking_exported
                          and (x.picking_type_id.id
                               == x.picking_type_id.warehouse_id.out_type_id.id
                               or
                               ('is_dropship' in self.env['stock.picking']._fields
                                and x.is_dropship
                                )
                               )
                          )
                # only send if tracking number field is non-empty
                .filtered('carrier_tracking_ref')
            )

            for picking in done_pickings_with_tracking:
                integration = picking.sale_id.integration_id
                if not integration:
                    continue

                if not integration.job_enabled('export_tracking'):
                    continue

                key = f'export_tracking_{picking.id}'
                integration = integration.with_context(company_id=integration.company_id.id)
                integration.with_delay(identity_key=key).export_tracking(picking)

        return res
