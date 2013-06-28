# -*- coding: utf-8 -*-
#
# The user interface module for cross-search available projects.
#
# (C) 2013 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2011/05/10
# @author: yosinobu@iij.ad.jp

from  pkg_resources import resource_filename

from genshi.builder import tag

from trac.core import *
from trac.web.chrome import INavigationContributor, ITemplateProvider, add_script, add_stylesheet
from trac.web.api import IRequestHandler, IRequestFilter
from trac.perm import IPermissionRequestor

from tracportal.api import IProjectListProvider
from tracportal.i18n import _
from tracportal.project_list.api import IProjectInfoProvider


class CrossSearchModule(Component):

    implements(INavigationContributor, IPermissionRequestor, IRequestHandler, ITemplateProvider)
    project_list_providers = ExtensionPoint(IProjectListProvider)
    project_info_providers = ExtensionPoint(IProjectInfoProvider)

    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        return 'cross_search'

    def get_navigation_items(self, req):
        if 'PORTAL_CROSS_SEARCH_VIEW' in req.perm:
            yield ('mainnav', 'cross_search',
                   tag.a(_('Cross Search'), href=req.href.cross_search(), accesskey=5))

    # IPermissionRequestor methods
    def get_permission_actions(self):
        return ['PORTAL_CROSS_SEARCH_VIEW']

    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info and req.path_info.startswith('/cross_search')

    def process_request(self, req):
        req.perm.require('PORTAL_CROSS_SEARCH_VIEW')
        data = {}
        add_script(req, 'tracportal/js/cross_search.js')
        if req.locale is not None:
            add_script(req, 'tracportal/js/messages/%s.js' % req.locale)
        add_stylesheet(req, 'tracportal/css/cross_search.css')
        projects = []
        for provider in self.project_list_providers:
            env_names = provider.get_env_name_list(['XML_RPC', 'SEARCH_VIEW'], [req.authname])
            if env_names:
                for env_name in env_names:
                    for info_provider in self.project_info_providers:
                        info = info_provider.get_info(env_name)
                        if info:
                            projects.append(info)
                            break
        targets = req.args.get('project', [])
        for p in projects:
            setattr(p, 'do_search', (p.env_name in targets))
        data['projects'] = projects
        data['q'] = req.args.get('q')
        data['filters'] = {
            'ticket': req.args.get('ticket', 'on'),
            'changeset': req.args.get('changeset', 'on'),
            'milestone': req.args.get('milestone', 'on'),
            'wiki': req.args.get('wiki', 'on'),
        }
        data['ignore_trac_default'] = req.args.get('ignore_default', 'on')
        data['num'] = req.args.get('num', 10)
        # data['_'] = _
        return "cross_search.html", data, None

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        return [('tracportal', resource_filename('tracportal', 'htdocs'))]

    def get_templates_dirs(self):
        return [resource_filename('tracportal.search', 'templates')]


class RedirectCrossSearch(Component):
    """Redirect a search uri(/search) to cross search uri(/cross_search)."""
    implements(IRequestFilter)

    # IRequestFilter methods

    def pre_process_request(self, req, handler):
        if req.path_info.startswith('/search'):
            req.redirect('%s?%s' % (req.href('/cross_search'), req.query_string))
        return handler

    def post_process_request(self, req, template, data, content_type):
        return template, data, content_type

