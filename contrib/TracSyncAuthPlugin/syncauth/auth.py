# -*- coding: utf-8 -*-
#
# (C) 2011 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2011/02/01
# @author: yosinobu
"""Trac component for automatically authentication."""

import sys
import time

from trac.core import Component, implements
from trac.web.api import IRequestFilter, IAuthenticator, IRequestHandler
from trac.config import Option, IntOption
from trac.web.auth import LoginModule
from trac.env import open_environment


class SyncAuth(Component):

    implements(IAuthenticator, IRequestFilter, IRequestHandler)

    auth_cookie_lifetime = IntOption('trac', 'auth_cookie_lifetime', 0)
    auth_cookie_path = Option('trac', 'auth_cookie_path', '')
    central_env_path = Option('syncauth', 'central_env', '', 'Trac environment path of management authentication.')

    # IAuthenticator methods

    def authenticate(self, req):
        if req.path_info.startswith('/chrome') or self.env.path == self.central_env_path:
            return None

        remote_user = LoginModule(self.env).authenticate(req)
        if remote_user:
            return remote_user

        cookie = None
        if req.incookie.has_key('trac_auth') and self.central_env_path:
            cookie = req.incookie['trac_auth']
            try:
                env = open_environment(self.central_env_path, use_cache=True)
                remote_user = self._cookie_to_name(env, req, cookie)
            except Exception, e:
                self.log.warn(e)

        if remote_user and cookie:
            req.authname = remote_user
            req.environ['REMOTE_USER'] = remote_user
            self._do_login(remote_user, req, cookie)
        return remote_user

    # IRequestFilter methods

    def pre_process_request(self, req, handler):
        if req.method == 'GET' and req.path_info.startswith('/login') and self.central_env_path:
            if not req.incookie.has_key('trac_auth'):
                try:
                    env = open_environment(self.central_env_path, use_cache=True)
                    LoginModule(env)._do_login(req)
                    return self
                except Exception, e:
                    self.log.warn(e)
        return handler

    def post_process_request(self, req, template, data, content_type):
        return template, data, content_type

    # IRequestHandler methods

    def match_request(self, req):
        return False

    def process_request(self, req):
        """Redirect only. does not authenticate in the current project."""
        LoginModule(self.env)._redirect_back(req)

    # Internal methods

    def _do_login(self, remote_user, req, cookie):
        # update the session information in database
        @self.env.with_transaction()
        def store_session_cookie(db):
            cursor = db.cursor()
            # Delete cookies older than 10 days
            cursor.execute("DELETE FROM auth_cookie WHERE time < %s",
                           (int(time.time()) - 86400 * 10,))
            cursor.execute("INSERT INTO auth_cookie (cookie,name,ipnr,time) "
                           "VALUES (%s, %s, %s, %s)",
                           (cookie.value, remote_user, req.remote_addr,
                            int(time.time())))
        # update the session cookie
        req.outcookie['trac_auth'] = cookie.value
        del req.outcookie['trac_auth']['expires']
        req.outcookie['trac_auth']['path'] = self.auth_cookie_path or req.base_path or '/'
        if self.env.secure_cookies:
            req.outcookie['trac_auth']['secure'] = True
        if sys.version_info >= (2, 6):
            req.outcookie['trac_auth']['httponly'] = True
        if self.auth_cookie_lifetime > 0:
            req.outcookie['trac_auth']['expires'] = self.auth_cookie_lifetime

    def _cookie_to_name(self, env, req, cookie):
        check_ip = env.config.getbool('trac', 'check_auth_ip', 'false')
        db = env.get_db_cnx()
        cursor = db.cursor()
        if check_ip:
            cursor.execute("SELECT name FROM auth_cookie "
                           "WHERE cookie=%s AND ipnr=%s",
                           (cookie.value, req.remote_addr))
        else:
            cursor.execute("SELECT name FROM auth_cookie WHERE cookie=%s",
                           (cookie.value,))
        row = cursor.fetchone()
        if row and len(row) > 0:
            return row[0]
        return None
