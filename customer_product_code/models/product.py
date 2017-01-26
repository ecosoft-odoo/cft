# -*- coding: utf-8 -*-
###############################################################################
#
#   customer_product_code for Odoo
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import osv, fields
from openerp import SUPERUSER_ID

class product_template(osv.Model):
    _inherit = "product.template"
    _order = "default_code,name"
    _columns = {
        'product_customer_code_ids': fields.one2many('product.customer.code',
                                                     'product_id',
                                                     'Customer Codes'),
        'default_code': fields.related('product_variant_ids', 'default_code', type='char', string='Internal Reference', store=True),
    }

class product_product(osv.Model):
    _inherit = "product.product"

    def _product_partner_ref(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for p in self.browse(cr, uid, ids, context=context):
            data = self._get_partner_code_name(cr, uid, [], p, context.get('partner_id', None), context=context)
            if not data['code']:
                data['code'] = p.code
            if not data['name']:
                data['name'] = p.name
            res[p.id] = (data['code'] and ('['+data['code']+'] ') or '') + (data['name'] or '')
        return res
        
    def _get_partner_code_name(self, cr, uid, ids, product, partner_id, context=None):
        if context.get('type', False) == 'in_invoice':
            for supinfo in product.seller_ids:
                if supinfo.name.id == partner_id:
                    return {'code': supinfo.product_code or product.default_code, 'name': supinfo.product_name or product.name}
        else:
            for buyinfo in product.product_customer_code_ids:
                if buyinfo.partner_id.id == partner_id:
                    return {'code': buyinfo.product_code or product.default_code, 'name': buyinfo.product_name or product.name}
        res = {'code': product.default_code, 'name': product.name}
        return res

    _columns = {
        'partner_ref' : fields.function(_product_partner_ref, type='char', string='Customer ref'),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default['product_customer_code_ids'] = False
        res = super(product_product, self).copy(
            cr, uid, id, default=default, context=context)
        return res

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []

        def _name_get(d):
            name = d.get('name','')
            code = context.get('display_default_code', True) and d.get('default_code',False) or False
            base_product = d.get('product_obj', False)
            if code:
                if context.get('type', False) == 'out_invoice' and base_product and not d.get('has_customer'):
                    name = '[%s] %s' % (base_product.default_code,base_product.name)
                else:
                   name = '[%s] %s' % (code,name)
            return (d['id'], name)
        partner_id = context.get('partner_id', False)
        if partner_id:
            partner_ids = [partner_id, self.pool['res.partner'].browse(cr, user, partner_id, context=context).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights(cr, user, "read")
        self.check_access_rule(cr, user, ids, "read", context=context)

        result = []
        for product in self.browse(cr, SUPERUSER_ID, ids, context=context):
            variant = ", ".join([v.name for v in product.attribute_value_ids])
            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            buyers = []
            if partner_ids:
                sellers = filter(lambda x: x.name.id in partner_ids, product.seller_ids)
                buyers = filter(lambda x: x.partner_id.id == partner_id, product.product_customer_code_ids)
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and "%s (%s)" % (s.product_name, variant) or False
                    mydict = {
                              'id': product.id,
                              'name': seller_variant or name,
                              'default_code': s.product_code or product.default_code,
                              }
                    result.append(_name_get(mydict))
            elif buyers:
                for b in buyers:
                    mydict = {
                              'id': product.id,
                              'name': b.product_name or product.name,
                              'default_code': b.product_code or product.default_code,
                              'product_obj': product,
                              'has_customer': True
                              }
                    result.append(_name_get(mydict))
            else:
                mydict = {
                          'id': product.id,
                          'name': name,
                          'default_code': product.default_code,
                          }
                result.append(_name_get(mydict))
        return result


    def name_search(self, cr, user, name='', args=None, operator='ilike',
                    context=None, limit=80):
        res = super(product_product, self).name_search(
            cr, user, name, args, operator, context, limit)
        if not context:
            context = {}
        product_customer_code_obj = self.pool.get('product.customer.code')
        if not res:
            ids = []
            partner_id = context.get('partner_id', False)
            if partner_id:
                id_prod_code = \
                    product_customer_code_obj.search(cr, user,
                                                     [('product_code',
                                                       '=', name),
                                                         ('partner_id', '=',
                                                          partner_id)],
                                                     limit=limit,
                                                     context=context)

                id_prod = id_prod_code and product_customer_code_obj.browse(
                    cr, user, id_prod_code, context=context) or []
                for ppu in id_prod:
                    ids.append(ppu.product_id.id)
            if ids:
                res = self.name_get(cr, user, ids, context)
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: