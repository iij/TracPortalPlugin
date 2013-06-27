# -*- coding: utf-8 -*-
#
# Interceptor for creating a new Trac project.
#
# (C) 2013 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2013/01/27
# @author: yosinobu@iij.ad.jp

from trac.core import Interface


class IProjectCreationInterceptor(Interface):

    @staticmethod
    def pre_process(project_info, owner_info):
        """Call this handler before a creating Trac project.
        Return value is list of Options.
        This value are added to options when creating the Trac project.
        One of Options is tuple which in section name, option's key, option's value.
        e.x.) [('trac', 'authz_file', '/path/to/authz_file')]

        :param project_info: the project information.(ID, name, description)
        :param owner_info: the project owner information.(user ID, full name, email)
        """

    @staticmethod
    def post_process(project_info, owner_info, env):
        """Call this handler after the created Trac project.

        :param project_info: the project information.(ID, name, description)
        :param owner_info: the project owner information.(user ID, full name, email)
        :param env: the created Trac environment object.
        """
