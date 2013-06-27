# -*- coding: utf-8 -*-
#
# Trac Project List API for Trac Portal Plugin.
#
# (C) 2011 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2011/01/27
# @author: yosinobu

import os
import time
from datetime import datetime

from trac.core import *
from trac.config import IntOption
from trac.env import open_environment
from trac.versioncontrol.api import DbRepositoryProvider
from trac.resource import ResourceNotFound
from trac.util.datefmt import localtz, to_datetime

from tracportal.api import IProjectListProvider
from tracportal.core import get_trac_env_parent_dir
from tracportal.i18n import _
from tracportal.util import to_tractime
from tracportal.project_list.model import ProjectActivity, ProjectInfo


class IProjectActivityDataProvider(Interface):
    """Extension point interface for adding sources for project activity data
    project_list."""

    @staticmethod
    def get_activity_data(env_name, beginning, end):
        """Return a activity data of the project."""


class DefaultActivityDataProvider(Component):

    implements(IProjectActivityDataProvider)
    project_list_providers = ExtensionPoint(IProjectListProvider)

    # Trac options
    period = IntOption('tracportal', 'project_activity_assessment_period', 30,
                       doc=_('Number of days to evaluate the project activity.'))

    # IProjectActivityDataProvider methods
    def get_activity_data(self, env_name, beginning, end):
        """プロジェクトのアクティビティを返す．

        データは，まずDBのキャッシュを取得し，期限が切れていれば，
        Trac の APIモジュールで取得する．
        (ローカルにあるプロジェクトのみ取得可能．)
        """
        activity = None
        try:
            activity = ProjectActivity(self.env, env_name)
        except ResourceNotFound, e:
            self.log.debug(e)
            activity = ProjectActivity(self.env)
        if not activity.is_expired():
            return activity
        env = None
        parent_dir = get_trac_env_parent_dir(self.env)
        env_dir = os.path.join(parent_dir, env_name)
        try:
            env = open_environment(env_dir, True)
        except Exception, e:
            # if needs_upgrade is True, raise Exception.
            self.log.warn("Cannot load a project Environment '%s', "
                          "Error: %s" % (env_dir, e))
            return None
        (activity.changes, activity.changes_month) = self._get_rev_count(env, beginning, end)
        (activity.tickets, activity.tickets_closed, activity.tickets_month,
         activity.tickets_closed_month) = self._get_ticket_count(env, beginning, end)
        if activity.exists:
            activity.update()
        else:
            activity.env_name = env_name
            activity.insert()
        return activity

    # Internal methods
    def _get_rev_count(self, env, beginning, end):
        revisions = 0
        total_revisions = 0
        provider = DbRepositoryProvider(env)
        repos = provider.get_repositories()
        for r in repos:
            repo = None
            if len(r) is 2 and 'alias' not in r[1]:
                repo = env.get_repository(r[0])
            if repo:
                try:
                    for changeset in repo.get_changesets(to_datetime(0), end):
                        if changeset.date > beginning:
                            revisions += 1
                        total_revisions += 1
                except Exception, e:
                    self.log.warn('%s' % str(e))
        return total_revisions, revisions

    @staticmethod
    def _get_ticket_count(env, beginning, end):
        if isinstance(beginning, datetime):
            beginning = time.mktime(beginning.astimezone(localtz).timetuple())
        if isinstance(end, datetime):
            end = time.mktime(end.astimezone(localtz).timetuple())
        beginning = to_tractime(beginning)
        end = to_tractime(end)
        db = env.get_read_db()
        tickets = 0
        tickets_month = 0
        tickets_closed = 0
        tickets_closed_month = 0
        def get_one(sql):
            cursor = db.cursor()
            cursor.execute(sql)
            return cursor.fetchone()[0]
        # count tickets
        tickets = get_one("SELECT count(*) FROM ticket")
        # count closed tickets
        tickets_closed = get_one("SELECT count(*) FROM ticket_change "
                                 "WHERE field='status' AND newvalue='closed'")
        tickets_reopened = get_one("SELECT count(*) FROM ticket_change "
                                   "WHERE field='status' AND newvalue='reopened'")
        tickets_closed -= tickets_reopened
        # count tickets during a term.
        tickets_month = get_one("SELECT count(*) FROM ticket WHERE time>=%s AND time<=%s" % (beginning, end))
        # count closed ticket during a term.
        tickets_closed_month = get_one("SELECT count(*) FROM ticket_change "
                                       "WHERE field='status' AND newvalue='closed' "
                                       "AND time>=%s AND time <=%s" % (beginning, end))
        tickets_reopened_month = get_one("SELECT count(*) FROM ticket_change "
                                         "WHERE field='status' AND newvalue='reopened' "
                                         "AND time>=%s AND time <=%s" % (beginning, end))
        tickets_closed_month -= tickets_reopened_month
        return tickets, tickets_closed, tickets_month, tickets_closed_month


class IProjectInfoProvider(Interface):

    @staticmethod
    def get_info(env_name):
        """Return the project information.
        Elements:
          `id`: Environment name
          `name`: the project name
          `description`: the project description
          `url`: the project base url
        """


class DefaultProjectInfoProvider(Component):

    implements(IProjectInfoProvider)

    # IProjectInfoProvider methods
    def get_info(self, env_name):
        info = None
        try:
            info = ProjectInfo(self.env, env_name)
        except ResourceNotFound, e:
            self.log.debug(e)
            info = ProjectInfo(self.env)
        if not info.is_expired():
            return info
        env = None
        parent_dir = get_trac_env_parent_dir(self.env)
        env_dir = os.path.join(parent_dir, env_name)
        try:
            env = open_environment(env_dir, True)
        except Exception, e:
            # if needs_upgrade is True, raise Exception.
            self.log.warn("Cannot load a project Environment '%s', "
                          "Error: %s" % (env_dir, e))
            return None
        href = env.abs_href()
        if not href or href == '/':
            href = self.env.abs_href().replace(self.get_self_env_name(), env_name)
        if href.endswith('/'):
            href = href.rstrip('/')
        info.id = env_name
        info.name = env.project_name
        info.description = env.project_description
        info.url = href
        if info.exists:
            info.update()
        else:
            info.env_name = env_name
            info.insert()
        return info

    def get_self_env_name(self):
        return self.env.path.rstrip('/').split('/')[-1]
