# -*- coding: utf-8 -*-
#
# (C) 2011 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2011/01/27
# @author: yosinobu@iij.ad.jp
"""Provide list of Trac environment name."""

import os
import dircache

from trac.core import *
from trac.config import Option, ListOption
from trac.env import open_environment
from trac.perm import PermissionSystem
from tracportal.core import get_trac_env_parent_dir

try:
    import ldap
except ImportError, e:
    ldap = None


class IProjectListProvider(Interface):
    """Extension point interface for adding sources for project project_list."""

    @staticmethod
    def get_env_name_list(actions, users):
        """Return a list of environ name(id) of project.

        Return a list of trac environment name that this provider supports.
        Each value must be a [value1, value2] list.

        default value:
          :param :actions a list of action list. default value is ['TRAC_ADMIN'].
                          e.x, ['WIKI_VIEW', 'TICKET_VIEW'] means WIKI_VIEW `and' TICKET_VIEW.
          :param :users a list of user names. default value is ['anonymous', 'authenticated']
                        that means anonymous `or' authenticated user.
                        if users is None, users append a login user.
        """


class BasicProjectListProvider(Component):
    """Provide list of Trac environment name from the local filesystem."""

    implements(IProjectListProvider)

    # Trac options
    ignore_projects = ListOption('tracportal', 'ignore_projects')

    # class variables
    envkey = 'TRAC_ENV_PARENT_DIR'

    # IProjectListProvider methods
    def get_env_name_list(self, actions=None, users=None):
        projects = []
        if not actions:
            actions = ['TRAC_ADMIN']
        if not users:
            users = ['anonymous', 'authenticated']
        for env_name, env_path in self.get_env_paths():
            if env_name in self.ignore_projects:
                continue
            try:
                env = open_environment(env_path, True)
                ps = PermissionSystem(env)
                for user in users:
                    checks = [ps.check_permission(action, user) for action in actions]
                    self.log.debug('[%s] Checked permission: %s (env_name: %s, user: %s, actions: %s)' %
                                   (self.__class__, checks, env_name, user, actions))

                    if False not in checks:
                        projects.append(env_name)
                        break
            except TracError, e:
                self.log.error(e)
        return projects

    def get_env_paths(self):
        parent_dir = get_trac_env_parent_dir(self.env)
        if parent_dir:
            parent_dir = os.path.normpath(parent_dir)
        if not parent_dir or not os.path.isdir(parent_dir):
            self.log.warn('No such a Trac parent directory. %s' % parent_dir)
            return
        projects = dircache.listdir(parent_dir)[:]
        for name in projects:
            env_path = os.path.join(parent_dir, name)
            if not os.path.exists(os.path.join(env_path, 'VERSION')):
                continue
            yield (name, env_path)
