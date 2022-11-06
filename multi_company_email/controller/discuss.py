
from odoo import http
from odoo.exceptions import AccessError, UserError
from odoo.http import request
from werkzeug.exceptions import NotFound

from odoo.addons.mail.controllers.discuss import DiscussController

import logging
_logger = logging.getLogger(__name__)



class MCDiscussController(DiscussController):


    @http.route('/mail/message/post', methods=['POST'], type='json', auth='public')
    def mail_message_post(self, thread_model, thread_id, post_data, **kwargs):
        if thread_model == 'mail.channel':
            channel_partner_sudo = request.env['mail.channel.partner']._get_as_sudo_from_request_or_raise(
                request=request, channel_id=int(thread_id))
            thread = channel_partner_sudo.channel_id
        else:
            thread = request.env[thread_model].browse(int(thread_id)).exists()

        company_id = post_data.get('company_id') or request.env.company.id
        return thread.with_company(company_id).message_post(**{key: value for key, value in post_data.items() if
                                                               key in self._get_allowed_message_post_params()}).message_format()[0]