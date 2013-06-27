#! -*- coding: utf-8 -*-
#
# (C) 2013 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2013/05/15
# @author: yosinobu@iij.ad.jp
"""Notify project creation with ticket when the project created successfully."""

from datetime import datetime
from trac.config import Option

from trac.core import Component, implements
from trac.env import open_environment
from trac.ticket import Ticket

from tracportal.i18n import _
from tracportal.project.api import IProjectCreationInterceptor


class TicketNotificationSystem(Component):
    implements(IProjectCreationInterceptor)
    #options
    notify_env = Option('tracportal', 'notify_ticket_env',
                        default='/var/service/data/trac/projects/all',
                        doc='Trac environment for notify creation project by new ticket.')

    # IProjectCreationInterceptor methods

    def pre_process(self, project_info, owner_info):
        pass

    def post_process(self, project_info, owner_info, _env):
        env = open_environment(self.notify_env)
        ticket = Ticket(env)
        values = {
            'project_id': project_info['id'],
            'project_owner': owner_info['id'],
            'register_date': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'status': 'new',
            'summary': project_info['name'],
            'component': _('TracPortal created a new project.'),
            'description': project_info['descr'],
        }
        for k, v in values.items():
            ticket[k] = v
        ticket.insert()
