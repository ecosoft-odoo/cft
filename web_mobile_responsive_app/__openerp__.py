# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2015 - Present Ahmed Magdy, ITpedia Solutions, LLC
#    All Rights Reserved
#    Author: Ahmed Magdy <ahmed.magdy40@gmail.com>
#    Author: Nicholas Riegel <nicholasr@itpediasolutions.com>
#    Author: Abdulrahman Hamdy <abdulrahmanh@itpediasolutions.com>
#    Author: Mouhamed Oussama SAHLI <mouhameds@itpediasolutions.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
##############################################################################

{
    'name': 'Web Mobile Responsive App',
    'category': 'User Interface',
    'version': '1.0008',
    'license': 'GPL-3',
    'price': 399.99,
    'currency': 'EUR',
    'author': 'ITpedia Solutions, LLC and Ahmed Magdy',
    'website': 'https://itpediasolutions.com',
    'images': ['static/description/responsive.png'],
    'description': """
    Very powerful software for Odoo 8 allowing users to take full advantage of all
    Odoo 8 features, functionality, apps, and modules in a fully responsive web
    mobile user interface. Any app or module written for the Odoo 8 web client
    interface will automatically display in a mobile friendly responsive user
    interface!
    """,
    'depends': ['base', 'web', 'web_kanban', 'im_chat'],
    'data': [
        'views/responsive_templates.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
}
