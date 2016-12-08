# -*- coding: utf-8 -*-
#
# Web API module of Dashboard.
#
# (C) 2013 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2013/05/28
# @author: yosinobu@iij.ad.jp

try:
    import json
except ImportError:
    import simplejson as json

from trac.core import Component, implements, ExtensionPoint
from trac.web import IRequestHandler

from tracportal.api import IProjectListProvider
from tracportal.project_list.api import IProjectInfoProvider

__author__ = 'yosinobu@iij.ad.jp'


class DashboardAPIModule(Component):
    implements(IRequestHandler)

    project_list_providers = ExtensionPoint(IProjectListProvider)
    project_info_providers = ExtensionPoint(IProjectInfoProvider)

    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info and req.path_info.startswith('/dashboard/api/projects')

    def process_request(self, req):
        req.perm.require('PORTAL_DASHBOARD_VIEW')
        require_perms = ['XML_RPC']
        if req.path_info.endswith('/report'):
            require_perms.extend(['TICKET_VIEW', 'REPORT_VIEW'])
        elif req.path_info.endswith('/roadmap'):
            require_perms.extend(['TICKET_VIEW', 'ROADMAP_VIEW', 'MILESTONE_VIEW'])
        elif req.path_info.endswith('/timeline'):
            require_perms.extend(['TIMELINE_VIEW'])
        projects = []
        for provider in self.project_list_providers:
            env_names = provider.get_env_name_list(require_perms, [req.authname])
            if env_names:
                for env_name in env_names:
                    for info_provider in self.project_info_providers:
                        info = info_provider.get_info(env_name)
                        if info:
                            projects.append({
                                'id': info.id,
                                'name': info.name,
                                'description': info.description,
                                'url': info.url
                            })
                            break
        req.send(json.dumps(projects), 'application/json')
