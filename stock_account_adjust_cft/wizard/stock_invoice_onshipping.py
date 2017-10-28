from openerp import models, api, _
from openerp.exceptions import except_orm


class StockInvoiceOnshipping(models.TransientModel):
    _inherit = 'stock.invoice.onshipping'

    @api.multi
    def open_invoice(self):
        User = self.env.user
        if User.has_group('sale_group_adjust_cft.group_sale_marketing'):
            raise except_orm(
                _('Warning!'),
                _('Cannot create invoice.'))
        res = super(StockInvoiceOnshipping, self).open_invoice()
        return res
