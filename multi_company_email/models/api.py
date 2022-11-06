from odoo import api, _
from odoo.exceptions import AccessError
from odoo.tools import lazy_property


def monkey_patch(cls):
    """ Return a method decorator to monkey-patch the given class. """
    def decorate(func):
        name = func.__name__
        func.super = getattr(cls, name, None)
        setattr(cls, name, func)
        return func
    return decorate


# @monkey_patch(api.Environment)
# @lazy_property
@monkey_patch(api.Environment)
def signature(self):
        """
        Return the current company signature.
        """
        company_ids = self.context.get('allowed_company_ids', [])
        company_id = self.user.company_id
        if company_ids:
            if not self.su:
                user_company_ids = self.user.company_ids.ids
                if any(cid not in user_company_ids for cid in company_ids):
                    raise AccessError(_("Access to unauthorized or invalid companies."))
            company_id = self['res.company'].browse(company_ids[0])
        return self.user.with_company(company_id.id).signature_text
