# -*- coding: utf-8 -*-
#
# Web UI for "New Project".
#
# (C) 2013 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2013/05/06
# @author: yosinobu@iij.ad.jp

import os
import re

from genshi.builder import tag
from pkg_resources import resource_filename
from trac.config import Option
from trac.core import *
from trac.env import Environment
from trac.perm import IPermissionRequestor, PermissionSystem
from trac.web import Href
from trac.web.api import IRequestHandler
from trac.web.chrome import ITemplateProvider, INavigationContributor, add_stylesheet, add_warning
from trac.web.session import Session
from trac.wiki.admin import WikiAdmin

from tracportal.core import get_parent_base_url, get_trac_env_parent_dir
from tracportal.i18n import _
from tracportal.project.api import IProjectCreationInterceptor


class NewProject(Component):
    """Add a user interface of project creation, and add a "New Project" link in navigation area."""

    implements(ITemplateProvider, INavigationContributor, IRequestHandler, IPermissionRequestor)

    # pre process / post process
    interceptors = ExtensionPoint(IProjectCreationInterceptor)

    # options
    inherit_file = Option('tracportal', 'inherit_file',
                          doc=_('Inherit config file. When create a project, set the [inherit] file option'
                                ' in the project config.'))

    # validation messages
    message_required = _('[%(category)s] %(field_name)s is required.')
    message_invalid_character = _('[%(category)s] %(field_name)s is used invalid characters.'
                                  '(Usable characters: alphabet[a-z], number[0-9], underscore["_"])')
    message_startswith_alpha = _('[%(category)s] %(field_name)s need to start with alphabet[a-z].')

    # ITemplateProvider methods

    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        return [('tracportal', resource_filename('tracportal', 'htdocs'))]

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        return 'new_project'

    def get_navigation_items(self, req):
        if 'PORTAL_PROJECT_CREATE' in req.perm:
            yield ('mainnav', 'new_project', tag.a(_('New Project'), href=req.href('/new_project')))

    # IPermissionRequestor methods

    def get_permission_actions(self):
        return ['PORTAL_PROJECT_CREATE']

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info == '/new_project'

    def process_request(self, req):
        req.perm.require('PORTAL_PROJECT_CREATE')
        owner = {
            'id': req.args.get('owner_id', req.authname),
            'name': req.args.get('owner_name'),
            'email': req.args.get('owner_email'),
        }
        project = {
            'id': req.args.get('project_id', ''),
            'name': req.args.get('project_name', ''),
            'descr': req.args.get('project_descr', ''),
        }
        notices = []

        # ignore anonymous
        if owner['id'] == 'anonymous':
            owner['id'] = ''

        if req.method == 'GET':
            # set user name/email from session.
            session = Session(self.env, req)
            if not owner['name']:
                owner['name'] = session.get('name')
            if not owner['email']:
                owner['email'] = session.get('email')

        if req.method == 'POST':
            self.log.debug('New project request. owner: %s, project: %s', owner, project)
            try:
                # validation
                self.validate_owner(owner)
                self.validate_project(project)
                # pre processors
                options = []
                for interceptor in self.interceptors:
                    opts = interceptor.pre_process(project, owner)
                    if opts:
                        options.extend(list(opts))
                # project creation
                env = self._create_project(project, owner, options)
                # post processors
                for interceptor in self.interceptors:
                    interceptor.post_process(project, owner, env)
                url = env.abs_href()
                msg = _('Successfully create a project. Please access to [%(url)s].', url=url)
                notices.append(msg)
                env.shutdown()
            except TracError, e:
                add_warning(req, e.message)
            except ValidationError, e:
                add_warning(req, e.message)
            except ProjectAlreadyExists:
                add_warning(req, _('Project "%(project_id)s" already exists.', project_id=project['id']))

        # set web page contents.
        add_stylesheet(req, 'tracportal/css/new_project.css')
        # create transmission data for view(template).
        data = {
            'ctx': {
                'owner': owner,
                'project': project,
            },
            'notices': notices,
            '_': _,
        }
        return 'new_project.html', data, None

    def validate_owner(self, owner):
        kwargs = {
            'category': _('Project Owner'),
            'field_name': _('User ID'),
        }
        owner_id = owner.get('id', '')
        if not owner_id:
            raise ValidationError(_(self.message_required, **kwargs))
        if not re.match('^[\w\d\-]*$', owner_id):
            raise ValidationError(_(self.message_invalid_character, **kwargs))
        if not owner_id[0].isalpha():
            raise ValidationError(_(self.message_startswith_alpha, **kwargs))
        if not owner.get('email'):
            kwargs['field_name'] = _('Email')
            raise ValidationError(_(self.message_required, **kwargs))
        if not owner.get('name'):
            kwargs['field_name'] = _('Fullname')
            raise ValidationError(_(self.message_required, **kwargs))

    def validate_project(self, project):
        kwargs = {
            'category': _('Project Information'),
            'field_name': _('Project ID'),
        }
        project_id = project.get('id')
        if not project_id:
            raise ValidationError(_(self.message_required, **kwargs))
        if not re.match('^[a-z_\d\-]*$', project_id):
            raise ValidationError(_(self.message_invalid_character, **kwargs))
        if not project_id[0].isalpha():
            raise ValidationError(_(self.message_startswith_alpha, **kwargs))
        if not project.get('name'):
            kwargs['field_name'] = _('Project Name')
            raise ValidationError(_(self.message_required, **kwargs))

    def _create_project(self, project, owner, options):
        parent_dir = get_trac_env_parent_dir(self.env)
        env_path = os.path.join(parent_dir, project['id'])
        if os.path.exists(env_path):
            self.log.info("Project %s already exists", env_path)
            raise ProjectAlreadyExists()
        options.extend(self._generate_options(project))
        if self.inherit_file:
            options.append(('inherit', 'file', self.inherit_file,))
        env = Environment(env_path, create=True, options=options)
        self._load_wiki_pages(env)
        self._add_permission(env, owner)
        return env

    def _generate_options(self, project):
        options = []
        parent_base_url = get_parent_base_url(self.env)
        if parent_base_url:
            parent_href = Href(parent_base_url)
            url = parent_href(project['id'])
            options.append(('trac', 'base_url', url))
            options.append(('project', 'url', url))
        options.append(('project', 'name', project['name']))
        options.append(('project', 'descr', project['descr']))
        return options

    def _load_wiki_pages(self, env):
        pages = resource_filename('trac.wiki', 'default-pages')
        try:
            WikiAdmin(env).load_pages(pages)
            return True
        except Exception, e:
            self.log.error(e)
        return False

    def _add_permission(self, env, owner):
        system = PermissionSystem(env)
        try:
            system.grant_permission(owner['id'], 'TRAC_ADMIN')
            return True
        except Exception, e:
            self.log.error(e)
        return False


class ProjectAlreadyExists(Exception):
    def __init__(self): pass


class ValidationError(Exception): pass
