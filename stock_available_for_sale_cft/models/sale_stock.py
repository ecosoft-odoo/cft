# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.tools import float_compare
from openerp.tools.translate import _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def product_id_change_with_wh(
        self, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False,
        name='', partner_id=False, lang=False, update_tax=True,
        date_order=False, packaging=False, fiscal_position=False, flag=False,
        warehouse_id=False
    ):
        res = super(SaleOrderLine, self).product_id_change_with_wh(
            pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag,
            warehouse_id=warehouse_id)
        context = self._context.copy() or {}
        ProductUOM = self.env['product.uom']
        Product = self.env['product.product']

        if not product:
            return res

        # Set product uom in context to get sale available in current uom
        if 'product_uom' in res.get('value', {}):
            # Use the uom changed by super call
            context = dict(context, uom=res['value']['product_uom'])
        elif uom:
            # Fallback on selected
            context = dict(context, uom=uom)

        # Update of result obtained in super function
        Product = Product.with_context(context).browse(product)

        # Calling product_packaging_change function after updating UoM
        res_packing = self.with_context(context).product_packaging_change(
            pricelist, product, qty, uom, partner_id, packaging)
        warning_msgs = res_packing.get('warning') and \
            res_packing['warning']['message'] or ''

        if Product.type == 'product':
            # Determine if the product needs further check for stock
            # availibility
            is_available = self.with_context(context) \
                ._check_routing(Product, warehouse_id)

            # check if product is available, and if not: raise a warning,
            # but do this only for products that aren't processed in MTO
            if not is_available:
                uom_record = False
                if uom:
                    uom_record = ProductUOM.with_context(context).browse(uom)
                    if Product.uom_id.category_id.id != \
                       uom_record.category_id.id:
                        uom_record = False
                if not uom_record:
                    uom_record = Product.uom_id
                compute_qty = float_compare(
                    Product.sale_available, qty,
                    precision_rounding=uom_record.rounding)
                if compute_qty == -1:
                    warn_msg = _('You plan to sell %.2f %s but you only have \
                        %.2f %s available !\nThe real stock is %.2f %s. \
                        (without reservations)') % \
                        (qty, uom_record.name,
                         max(0, Product.sale_available), uom_record.name,
                         max(0, Product.qty_available), uom_record.name)
                    warning_msgs += _("Not enough stock ! : ") + warn_msg + \
                        "\n\n"
                    warning = {
                        'title': _('Configuration Error!'),
                        'message': warning_msgs
                    }
                    res.update({'warning': warning})
        return res
