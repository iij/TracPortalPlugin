#! -*- coding: utf-8 -*-
#
# (C) 2013 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2013/05/15
# @author: yosinobu@iij.ad.jp
"""Notify project owner with email when the project created successfully."""
from pkg_resources import resource_filename

from trac.core import Component, implements
from trac.notification import Notify, NotifyEmail
from trac.config import Option, ListOption
from trac.web.chrome import ITemplateProvider

from tracportal.i18n import _
from tracportal.project.api import IProjectCreationInterceptor


class ProjectCreationNotificationSystem(Component):
    implements(ITemplateProvider, IProjectCreationInterceptor)

    # options
    from_name = Option('tracportal', 'notify_email_from_name', doc=_('Sender name to use in notification emails.'))
    from_email = Option('tracportal', 'notify_email_from', doc=_('Sender address to use in notification emails.'))
    ccrcpts = ListOption('tracportal', 'notify_email_cc',
                         doc=_('Email address(es) to always send notifications to, '
                               'addresses can be seen by all recipients (Cc:).'))
    subject = Option('tracportal', 'notify_email_subject', default=_("Ready to start Trac project!"),
                     doc=_('Subject in notification emails.'))

    # ITemplateProvider methods

    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        return []

    # IProjectCreationInterceptor methods

    def pre_process(self, project_info, owner_info):
        pass

    def post_process(self, project_info, owner_info, env):
        if 'email' in owner_info:
            project_info['url'] = env.abs_href()
            support = {
                'name': self.from_name or self.env.project_name,
                'email': self.from_email or self.env.config.get('notification', 'smtp_from'),
            }
            notify_email = ProjectCreationNotifyEmail(self.env, (owner_info['email'],), tuple(self.ccrcpts),
                                                      project_info, owner_info, support)
            notify_email.notify('')


class ProjectCreationNotifyEmail(NotifyEmail):
    """Notification of a project creation."""
    template_name = 'project_creation_notify_email.txt'

    def __init__(self, env, torcpts, ccrcpts, project_info, owner_info, support):
        NotifyEmail.__init__(self, env)
        self.torcpts = torcpts
        self.ccrcpts = ccrcpts
        self.project_info = project_info
        self.owner_info = owner_info
        self.support = support
        self.subject = self.subject

    def get_recipients(self, resid):
        return (self.torcpts, self.ccrcpts,)

    def notify(self, resid, subject=None, author=None):
        if subject:
            self.subject = subject
        self.from_name = self.support['name']
        self.from_email = self.support['email']
        self.replyto_email = self.support['email']
        if self.data is None:
            self.data = {}
        self.data.update({
            'owner': self.owner_info,
            'project': self.project_info,
            'support': self.support,
        })
        Notify.notify(self, resid)