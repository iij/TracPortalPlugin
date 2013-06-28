# -*- coding: utf-8 -*-
#
# Data Models.
#
# (C) 2013 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2011/01/27
# @author: yosinobu@iij.ad.jp

import time

from trac.core import TracError
from trac.resource import ResourceNotFound
from trac.config import IntOption

from tracportal.util import to_unixtime
from tracportal.i18n import _


class ProjectActivity(object):

    IntOption('tracportal', 'project_activity_cache_ttl', 86400,
              _('Time to live of cache(sec) for project activity.'))

    def __init__(self, env, env_name=None, db=None):
        self.env = env
        self.env_name = env_name
        self.changes = 0
        self.changes_month = 0
        self.tickets = 0
        self.tickets_month = 0
        self.tickets_closed = 0
        self.tickets_closed_month = 0
        self.updated_at = 1000000000
        self.score = 0
        self.score_month = 0
        self._exists = False
        if env_name:
            if not db:
                db = self.env.get_read_db()
            cursor = db.cursor()
            cursor.execute("""
            SELECT id, changes, changes_month, tickets, tickets_month,
            tickets_closed, tickets_closed_month, updated_at
            FROM cache_projects_stats WHERE id=%s
            """, (env_name,))
            row = cursor.fetchone()
            if not row:
                raise ResourceNotFound(_('Project Activity %(name)s does not exist.',
                                         name=env_name))
            self._exists = True
            self.changes = row[1]
            self.changes_month = row[2]
            self.tickets = row[3]
            self.tickets_month = row[4]
            self.tickets_closed = row[5]
            self.tickets_closed_month = row[6]
            self.updated_at = to_unixtime((row[7] or self.updated_at))

    exists = property(fget=lambda self: self._exists)

    def get_total(self):
        return sum((self.changes, self.tickets, self.tickets_closed))

    def get_total_month(self):
        return sum((self.changes_month, self.tickets_month,
                   self.tickets_closed_month))

    def is_expired(self, updated_at=None):
        cache_ttl = self.env.config.getint('tracportal', 'project_activity_cache_ttl', 86400)
        updated_at = updated_at or self.updated_at
        if not updated_at:
            return False
        now = to_unixtime(time.time())
        return self.updated_at < (now - cache_ttl)

    def insert(self, db=None):
        """Insert a project activity data.

        The `db` argument is deprecated in favor of `with_transaction()`.
        """
        assert not self.exists, 'Cannot insert existing activity data.'
        if not self.env_name:
            raise TracError(_('Invalid Project ID (env_name) %s',
                              (self.env_name, )))

        @self.env.with_transaction(db)
        def do_insert(db):
            self.env.log.debug('Creating activity data %s' % self.env_name)
            cursor = db.cursor()
            cursor.execute("""
            INSERT INTO cache_projects_stats (id, changes, changes_month,
            tickets, tickets_month, tickets_closed, tickets_closed_month)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (self.env_name, self.changes, self.changes_month,
                  self.tickets, self.tickets_month, self.tickets_closed,
                  self.tickets_closed_month))

    def update(self, db=None):
        """Update a project activity data.

        The `db` argument is deprecated in favor of `with_transaction()`.
        """
        assert self.exists, 'Cannot update non-existent activity data.'
        if not self.env_name:
            raise TracError(_('Invalid Project ID (env_name) %s',
                              (self.env_name, )))

        @self.env.with_transaction(db)
        def do_update(db):
            self.env.log.debug('Updating activity data %s' % self.env_name)
            cursor = db.cursor()
            cursor.execute("""
            UPDATE cache_projects_stats SET changes=%s, changes_month=%s,
            tickets=%s, tickets_month=%s, tickets_closed=%s, tickets_closed_month=%s
            WHERE id=%s
            """, (self.changes, self.changes_month,
                  self.tickets, self.tickets_month, self.tickets_closed,
                  self.tickets_closed_month, self.env_name))

    def delete(self, db=None):
        """Delete the activity data.

        The `db` argument is deprecated in favor of `with_transaction()`.
        """

        assert self.exists, 'Cannot delete non-existent activity data.'
        if not self.env_name:
            raise TracError(_('Invalid Project ID (env_name) %s',
                              (self.env_name, )))

        @self.env.with_transaction(db)
        def do_delete(db):
            self.env.log.info('Deleting activity data %s' % self.env_name)
            cursor = db.cursor()
            cursor.execute("DELETE FROM cache_projects_stats WHERE id=%s",
                           (self.env_name,))


class ProjectInfo(object):

    IntOption('tracportal', 'project_info_cache_ttl', 86400,
              _('Time to live of cache(sec) for project information.'))

    def __init__(self, env, env_name=None, db=None):
        self.env = env
        self.id = env_name
        self.env_name = env_name
        self.name = None
        self.url = None
        self.description = None
        self.updated_at = 1000000000
        self._exists = False
        if env_name:
            if not db:
                db = self.env.get_read_db()
            cursor = db.cursor()
            cursor.execute("""
            SELECT id, name, url, description, updated_at
            FROM cache_projects
            WHERE id=%s
            """, (env_name,))
            row = cursor.fetchone()
            if not row:
                raise ResourceNotFound(_('Project Information %(name)s does not exist.',
                                         name=env_name))
            self._exists = True
            self.name = row[1]
            self.url = row[2]
            self.description = row[3]
            self.updated_at = to_unixtime(row[4])

    exists = property(fget=lambda self: self._exists)

    def is_expired(self, updated_at=None):
        cache_ttl = self.env.config.getint('tracportal', 'project_info_cache_ttl', 86400)
        updated_at = updated_at or self.updated_at
        if not updated_at:
            return False
        now = to_unixtime(time.time())
        return self.updated_at < (now - cache_ttl)

    def insert(self, db=None):
        """Insert a project information.

        The `db` argument is deprecated in favor of `with_transaction()`.
        """
        assert not self.exists, 'Cannot insert existing project information.'
        if not self.id:
            raise TracError(_('Invalid Project ID (env_name) %s',
                              (self.id,)))

        @self.env.with_transaction(db)
        def do_insert(db):
            self.env.log.debug('Creating project information %s' % self.id)
            cursor = db.cursor()
            cursor.execute("""
            INSERT INTO cache_projects (id, name, url, description)
            VALUES (%s, %s, %s, %s)
            """, (self.id, self.name, self.url, self.description))

    def update(self, db=None):
        """Update a project information.

        The `db` argument is deprecated in favor of `with_transaction()`.
        """
        assert self.exists, 'Cannot update non-existent project information.'
        if not self.id:
            raise TracError(_('Invalid Project ID (env_name) %s',
                              (self.id, )))

        @self.env.with_transaction(db)
        def do_update(db):
            self.env.log.debug('Updating project information %s' % self.id)
            cursor = db.cursor()
            cursor.execute("""
            UPDATE cache_projects SET name=%s, url=%s, description=%s
            WHERE id=%s
            """, (self.name, self.url, self.description, self.id))

    def delete(self, db=None):
        """Delete the project information.

        The `db` argument is deprecated in favor of `with_transaction()`.
        """

        assert self.exists, 'Cannot delete non-existent project information.'
        if not self.id:
            raise TracError(_('Invalid Project ID (env_name) %s',
                              (self.id, )))

        @self.env.with_transaction(db)
        def do_delete(db):
            self.env.log.info('Deleting project information %s' % self.id)
            cursor = db.cursor()
            cursor.execute("DELETE FROM cache_projects WHERE id=%s",
                           (self.id,))
