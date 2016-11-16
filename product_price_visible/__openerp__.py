###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#                 2016 Ecosoft Co. Ltd.
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: isaac (isaac@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
#~ "security/ir.model.access.csv",
{
    "name": "Product Price Visible",
    "version": "8.0.0.1.6",
    "author": "Vauxoo",
              "Ecosoft Co. Ltd."
    "category": "Product",
    "website": "",

    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_account",
    ],
    "data": [
        "security/product_price_visible.xml",
        "product_view.xml"
    ],
    "demo": [
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: