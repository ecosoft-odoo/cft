# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.addons.base_geolocalize.models.res_partner import geo_find
from openerp import tools


# Overwrite Method
def geo_query_address(street=None, township=None, district=None, province=None,
                      zip=None, country=None):
    addr = []
    if street:
        addr.append(street.strip())
    if township:
        addr.append(township.strip())
    if district:
        addr.append(district.strip())
    if province:
        addr.append(province.strip())
    if zip:
        addr.append(zip.strip())
    if country:
        addr.append(country.strip())
    return tools.ustr(', '.join(filter(None, addr)))


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Overwrite Method
    @api.model
    def _address_as_string(self):
        addr = []
        if self.street:
            addr.append(self.street.strip())
        if self.township_id:
            addr.append(self.township_id.name.strip())
        if self.district_id:
            addr.append(self.district_id.name.strip())
        if self.province_id:
            addr.append(self.province_id.name.strip())
        if self.zip:
            addr.append(self.zip.strip())
        if self.country_id:
            addr.append(self.country_id.name.strip())
        if not addr:
            raise Warning(
                _("Address missing on partner '%s'.") % self.name)
        address = ' '.join(addr)
        return address

    # Overwrite method
    @api.multi
    def geo_localize(self):
        for partner in self:
            if not partner:
                continue
            result = geo_find(geo_query_address(
                street=partner.street,
                township=partner.township_id.name,
                district=partner.district_id.name,
                province=partner.province_id.name,
                zip=partner.zip,
                country=partner.country_id.name))
            if result:
                partner.write({
                    'partner_latitude': result[0],
                    'partner_longitude': result[1],
                    'date_localization': fields.Date.context_today(self)
                })
        return True
