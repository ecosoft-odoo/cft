# -*- encoding: utf-8 -*-
import openerp.addons.jasper_reports as jasper_reports


def report_product_stock_ledger_parser(cr, uid, ids, data, context):
    parameters = data['parameters']
    return {
        'parameters': {
            'product_id': parameters.get('product_id', -1),
            'from_date': parameters.get('from_date', ''),
            'to_date': parameters.get('to_date', ''),
        }
    }


jasper_reports.report_jasper(
    'report.report.product.normal.stock.ledger',
    'product.product',
    parser=report_product_stock_ledger_parser
)
