from . import models
from . import controller

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _get_partner_info(env)


def _get_partner_info(env):
    env.cr.execute("""SELECT id, email FROM res_partner;""")
    print("LETS GET THE INFO TO SAVE")
    partner_info_list = env.cr.dictfetchall()
    for partner_dict in partner_info_list:
        partner = env['res.partner'].browse(partner_dict.get('id'))
        for company in env['res.company'].search([]):
            partner.with_company(company.id).write({'email': partner_dict.get('email')})
    print("EMAIL COMPLETE")
    env.cr.execute("""
                    SELECT id, signature FROM res_users;
                """)
    user_signature_list = env.cr.dictfetchall()
    for user_signature in user_signature_list:
        user = env['res.users'].browse(user_signature.get('id'))
        for company in env['res.company'].search([]):
            user.with_company(company.id).write({'signature_text': user_signature.get('signature')})
    env.cr.commit()

