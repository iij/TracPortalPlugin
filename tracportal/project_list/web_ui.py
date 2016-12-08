# -*- coding: utf-8 -*-
#
# User Interface Module for Trac Portal Plugin.
#
# (C) 2013 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2011/01/27
# @author: yosinobu@iij.ad.jp

from datetime import timedelta

from genshi.builder import tag
from  pkg_resources import resource_filename
from trac.config import Option, IntOption
from trac.core import *
from trac.perm import IPermissionRequestor
from trac.util.datefmt import to_datetime, utc
from trac.web.api import IRequestHandler
from trac.web.chrome import ITemplateProvider, INavigationContributor, \
    add_stylesheet, add_script

from tracportal.api import IProjectListProvider
from tracportal.i18n import _
from tracportal.project_list.api import IProjectActivityDataProvider, IProjectInfoProvider


class ProjectListModule(Component):
    implements(INavigationContributor, IPermissionRequestor, ITemplateProvider,
               IRequestHandler)

    project_list_providers = ExtensionPoint(IProjectListProvider)
    project_activity_providers = ExtensionPoint(IProjectActivityDataProvider)
    project_info_providers = ExtensionPoint(IProjectInfoProvider)

    period = IntOption('tracportal', 'project_activity_assessment_period', 30,
                       doc=_('Number of days to evaluate the project activity.'))
    link_suffix = Option('tracportal', 'project_list_link_url_suffix', '',
                         doc=_('Path to be appended to the project url in project list page. '
                               '(e.x, if need login, set "/login" value in this option.)'))

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        return 'available_projects'

    def get_navigation_items(self, req):
        if 'PORTAL_PROJECT_LIST_VIEW' in req.perm:
            yield ('mainnav', 'available_projects',
                   tag.a(_('Available Projects'),
                         href=req.href('/projects/available')))

    # IPermissionRequestor methods

    def get_permission_actions(self):
        return ['PORTAL_PROJECT_LIST_VIEW']

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        return [('tracportal', resource_filename('tracportal', 'htdocs'))]

    def get_templates_dirs(self):
        return [resource_filename('tracportal.project_list', 'templates')]

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info in ['/projects', '/projects/available']

    def process_request(self, req):
        req.perm.require('PORTAL_PROJECT_LIST_VIEW')
        add_stylesheet(req, "tracportal/css/project_list.css")
        add_script(req, "tracportal/js/project_list.js")
        env_names = []
        projects = []
        for provider in self.project_list_providers:
            env_names = provider.get_env_name_list(['WIKI_VIEW'], [req.authname])
            if env_names:
                break
        for env_name in env_names:
            project = {
                'env_name': env_name,
                'info': None,
                'activity': None,
            }
            # project info
            for provider in self.project_info_providers:
                info = provider.get_info(env_name)
                if info:
                    project['info'] = info
                    break
            # project activity data
            end = to_datetime(None, utc)
            beginning = end - timedelta(self.period)
            for provider in self.project_activity_providers:
                activity = provider.get_activity_data(env_name, beginning, end)
                if activity:
                    project['activity'] = activity
                    break
            if 'info' not in project or not project['info']:
                self.log.warn('Cannot get a project info %s' % env_name)
                continue
            if 'activity' not in project or not project['activity']:
                self.log.warn('Cannot get a project activity %s' % env_name)
                continue
            projects.append(project)
        # calculate activity
        total = max([p['activity'].get_total() for p in projects] or [0])
        total_month = max([p['activity'].get_total_month() for p in projects] or [0])
        rate = (total is not 0) and (100.0 / float(total)) or 0
        rate_month = (total_month is not 0) and (100.0 / float(total_month)) or 0
        for p in projects:
            p['activity'].score = int(float(p['activity'].get_total()) * rate)
            p['activity'].score_month = int(float(p['activity'].get_total_month()) * rate_month)
        projects.sort(lambda x, y: x['activity'].score_month == y['activity'].score_month
                                   and (y['activity'].score - x['activity'].score)
                                   or (y['activity'].score_month - x['activity'].score_month))
        data = {
            'type': 'available',
            'projects': projects,
            'title': _('Available Projects'),
            'link_suffix': self.link_suffix,
            '_': _,
        }
        return 'project_list.html', data, None


class PublicProjectListModule(Component):
    implements(INavigationContributor, IPermissionRequestor, ITemplateProvider, IRequestHandler)

    project_list_providers = ExtensionPoint(IProjectListProvider)
    project_activity_providers = ExtensionPoint(IProjectActivityDataProvider)
    project_info_providers = ExtensionPoint(IProjectInfoProvider)

    period = IntOption('tracportal', 'project_activity_assessment_period', 30,
                       doc=_('Number of days to evaluate the project activity.'))
    link_suffix = Option('tracportal', 'project_list_link_url_suffix', '',
                         doc=_('Path to be appended to the project url in project list page. '
                               '(e.x, if need login, set "/login" value in this option.)'))

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        return 'public_projects'

    def get_navigation_items(self, req):
        if 'PORTAL_PUBLIC_PROJECT_LIST_VIEW' in req.perm:
            yield ('mainnav', 'public_projects',
                   tag.a(_('Public Projects'),
                         href=req.href('/projects/public')))

    # IPermissionRequestor methods

    def get_permission_actions(self):
        return ['PORTAL_PUBLIC_PROJECT_LIST_VIEW']

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        return [('tracportal', resource_filename('tracportal', 'htdocs'))]

    def get_templates_dirs(self):
        return [resource_filename('tracportal.project_list', 'templates')]

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info == '/projects/public'

    def process_request(self, req):
        req.perm.require('PORTAL_PUBLIC_PROJECT_LIST_VIEW')
        add_stylesheet(req, "tracportal/css/project_list.css")
        add_script(req, "tracportal/js/project_list.js")
        env_names = []
        projects = []
        for provider in self.project_list_providers:
            env_names = provider.get_env_name_list(['WIKI_VIEW'], ['anonymous', 'authenticated'])
            if env_names:
                break
        for env_name in env_names:
            project = {
                'env_name': env_name,
                'info': None,
                'activity': None,
            }
            # project info
            for provider in self.project_info_providers:
                info = provider.get_info(env_name)
                if info:
                    project['info'] = info
                    break
            # project activity data
            end = to_datetime(None, utc)
            beginning = end - timedelta(self.period)
            for provider in self.project_activity_providers:
                activity = provider.get_activity_data(env_name, beginning, end)
                if activity:
                    project['activity'] = activity
                    break
            if 'info' not in project or not project['info']:
                self.log.warn('Cannot get a project info %s' % env_name)
                continue
            if 'activity' not in project or not project['activity']:
                self.log.warn('Cannot get a project activity %s' % env_name)
                continue
            projects.append(project)
        # calculate activity
        total = max([p['activity'].get_total() for p in projects] or [0])
        total_month = max([p['activity'].get_total_month() for p in projects] or [0])
        rate = (total is not 0) and (100.0 / float(total)) or 0
        rate_month = (total_month is not 0) and (100.0 / float(total_month)) or 0
        for p in projects:
            p['activity'].score = int(float(p['activity'].get_total()) * rate)
            p['activity'].score_month = int(float(p['activity'].get_total_month()) * rate_month)
        projects.sort(lambda x, y: x['activity'].score_month == y['activity'].score_month
                                   and (y['activity'].score - x['activity'].score)
                                   or (y['activity'].score_month - x['activity'].score_month))
        data = {
            'type': 'public',
            'projects': projects,
            'title': _('Public Projects'),
            'link_suffix': self.link_suffix,
            '_': _,
        }
        return 'project_list.html', data, None
