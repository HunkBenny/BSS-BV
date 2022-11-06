# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sh_purchase_count = fields.Integer(
        string='# of Purchases', compute='_compute_purchase', readonly=True)

    def _compute_purchase(self):
        purchase_order_obj = self.env['purchase.order']
        if self:
            for rec in self:
                rec.sh_purchase_count = 0
                po_count = purchase_order_obj.search_count(
                    [('sh_sale_order_id', '=', rec.id)])
                rec.sh_purchase_count = po_count

    def sh_action_view_purchase(self):
        purchase_order_obj = self.env['purchase.order']
        if self and self.id:
            if self.sh_purchase_count == 1:
                po_search = purchase_order_obj.search(
                    [('sh_sale_order_id', '=', self.id)], limit=1)
                if po_search:
                    return {
                        "type": "ir.actions.act_window",
                        "res_model": "purchase.order",
                        "views": [[False, "form"]],
                        "res_id": po_search.id,
                        "target": "self",
                    }
            if self.sh_purchase_count > 1:
                po_search = purchase_order_obj.search(
                    [('sh_sale_order_id', '=', self.id)])
                if po_search:
                    action = self.env.ref('purchase.purchase_rfq').read()[0]
                    action['domain'] = [('id', 'in', po_search.ids)]
                    action['target'] = 'self'
                    return action

    def sh_create_po(self):
        """
            this method fire the action and open create purchase order wizard
        """
        view = self.env.ref('sh_so_po.sh_purchase_order_wizard')
        context = self.env.context
        return {
            'name': 'Create Purchase Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }

    def action_check(self):
        if self.order_line:
            for line in self.order_line:
                line.tick = True

    def action_uncheck(self):
        if self.order_line:
            for line in self.order_line:
                line.tick = False


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tick = fields.Boolean(string="Select Product")

    def btn_tick_untick(self):
        if self.tick == True:
            self.tick = False
        else:
            self.tick = True


