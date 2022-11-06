/** @odoo-module **/

import {
    registerInstancePatchModel,
} from '@mail/model/model_core';
import { addLink, escapeAndCompactTextContent, parseAndTransform } from '@mail/js/utils';


var session = require('web.session');

registerInstancePatchModel('mail.composer_view', '/multi_company_email/static/src/js/composer_view.js', {

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _getMessageData() {
        let res = this._super(...arguments);
        res.company_id = session.user_context.allowed_company_ids[0];
        return res
    },
});
