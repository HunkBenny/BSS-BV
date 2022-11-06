from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class Partners(models.Model):
    _inherit = 'res.partner'

    email = fields.Char(company_dependent=True)
    company_dependent_email = fields.Char(company_dependent=True)

    @api.model_create_multi
    def create(self, vals_list):
        partners = super(Partners, self).create(vals_list)
        for partner in partners.filtered(lambda p: p.email):
            email = partner.email
            for company_id in self.env['res.company'].sudo().search([]):
                partner.sudo().with_company(company_id.id).email = email
        return partners

    def write(self, vals):
        if 'email' in vals and not self.env.context.get('force_partner_email'):
            for partner in self.filtered(lambda p: not p.user_ids):
                for company_id in self.env['res.company'].sudo().search([]):
                    partner.sudo().with_company(company_id.id).with_context(force_partner_email=True).email = vals.get('email')
        return super(Partners, self).write(vals)

