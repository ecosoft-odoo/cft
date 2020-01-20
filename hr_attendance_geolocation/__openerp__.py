# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2019 Eficent Business and IT Consulting Services S.L..
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

{
    'name': 'Hr Attendance Geolocation',
    'summary': """
        With this module the geolocation of the user is tracked at the
        check-in/check-out step""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Eficent Business and IT Consulting Services S.L.,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'decimal_precision',
        'hr_attendance',
    ],
    'data': [
        'views/assets.xml',
        'views/hr_attendance_views.xml',
        'data/location_data.xml',
    ],
}
