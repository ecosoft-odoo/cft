# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2013 OpenERP S.A. (<http://openerp.com>).
#
#    Copyright (C) 2011-2015 Nevpro Business Solutions Pvt Ltd. (<http://www.nevpro.co.in>).
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

import logging
import openerp
from openerp.osv import fields, osv, orm
from datetime import date,datetime,time,timedelta
from openerp import SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _
from openerp.http import Response
from openerp import http

_logger = logging.getLogger(__name__)

# minutes a session stays valid without heartbeat
SESSION_MINUTES = 5


class Home(openerp.addons.web.controllers.main.Home):
	@http.route('/web/login', type='http', auth="none")
	def web_login(self, redirect=None, **kw):
		openerp.addons.web.controllers.main.ensure_db()
		
		if request.httprequest.method == 'GET' and redirect and request.session.uid:
			return http.redirect_with_hash(redirect)
		
		if not request.uid:
			request.uid = openerp.SUPERUSER_ID
		
		values = request.params.copy()
		if not redirect:
			redirect = '/web?' + request.httprequest.query_string
		values['redirect'] = redirect
		
		try:
			values['databases'] = http.db_list()
		except openerp.exceptions.AccessDenied:
			values['databases'] = None
		
		if request.httprequest.method == 'POST':
			old_uid = request.uid
			uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
			if uid is not False:
				return http.redirect_with_hash(redirect)
			request.uid = old_uid
			values['error'] = "Login failed due to one of the following reasons"
			values['error2'] = "- Wrong login/password"
			values['error3'] = "- User already logged in from another system"
		return request.render('web.login', values)


class Root_new(openerp.http.Root):
	def get_response(self, httprequest, result, explicit_session):
		if isinstance(result, Response) and result.is_qweb:
			try:
				result.flatten()
			except(Exception), e:
				if request.db:
					result = request.registry['ir.http']._handle_exception(e)
				else:
					raise
		
		if isinstance(result, basestring):
			response = Response(result, mimetype='text/html')
		else:
			response = result
		
		if httprequest.session.should_save:
			self.session_store.save(httprequest.session)
		# We must not set the cookie if the session id was specified using a http header or a GET parameter.
		# There are two reasons to this:
		# - When using one of those two means we consider that we are overriding the cookie, which means creating a new
		#   session on top of an already existing session and we don't want to create a mess with the 'normal' session
		#   (the one using the cookie). That is a special feature of the Session Javascript class.
		# - It could allow session fixation attacks.
		if not explicit_session and hasattr(response, 'set_cookie'):
			# no max_age: browser session cookie, closing the browser requires a new login
			response.set_cookie('session_id', httprequest.session.sid)
		
		return response

root = Root_new()
openerp.http.Root.get_response = root.get_response


class res_users(osv.osv):
	_inherit = 'res.users'
	
	_columns = { 
		'session_id' : fields.char('Session ID', size=100),
		'expiration_date' : fields.datetime('Expiration Date'),
		'logged_in': fields.boolean('Logged in'),
		}
	
	def _login(self, db, login, password):
		user_id = super(res_users,self)._login(db, login, password)
		if not user_id:
			return user_id

		cr = self.pool.cursor()
		cr.autocommit(True)
		try:
			session_id = request.httprequest.session.sid
			temp_browse = self.browse(cr, SUPERUSER_ID, user_id)
			if isinstance(temp_browse, list): temp_browse = temp_browse[0]
			exp_date = temp_browse.expiration_date
			if exp_date and temp_browse.session_id:
				exp_date = datetime.strptime(exp_date,"%Y-%m-%d %H:%M:%S")
				# block only another session that is still alive, an expired one is replaced
				if exp_date >= datetime.utcnow() and temp_browse.session_id != session_id:
					raise openerp.exceptions.AccessDenied()
			self.save_session(cr,user_id)
		except openerp.exceptions.AccessDenied:
			user_id = False
			_logger.warn("User %s is already logged in into the system!", login)
			_logger.warn("Multiple sessions are not allowed for security reasons!")
		finally:
			cr.close()
	
		return user_id


	#runs the update on its own autocommit cursor: no serialization failure
	#on res_users and no ORM cache invalidation like res.users.write()
	def _update_session(self, query, params):
		cr = self.pool.cursor()
		cr.autocommit(True)
		try:
			cr.execute(query, params)
		finally:
			cr.close()

	#clears session_id and session expiry from res.users
	def clear_session(self, cr, user_id):
		if isinstance(user_id, list): user_id = user_id[0]
		self._update_session("""
			UPDATE res_users SET session_id = '', expiration_date = NULL, logged_in = false
			 WHERE id = %s""", (user_id,))

	#insert session_id and session expiry into res.users
	def save_session(self, cr, user_id):
		if isinstance(user_id, list): user_id = user_id[0]
		exp_date = datetime.utcnow() + timedelta(minutes=SESSION_MINUTES)
		sid = request.httprequest.session.sid
		self._update_session("""
			UPDATE res_users SET session_id = %s, expiration_date = %s, logged_in = true
			 WHERE id = %s""", (sid, exp_date, user_id))

	#schedular function to validate users session
	def validate_sessions(self, cr, uid):
		cr.execute("""
			UPDATE res_users SET session_id = '', expiration_date = NULL, logged_in = false
			 WHERE expiration_date < %s""", (datetime.utcnow(),))
