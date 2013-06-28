# -*- coding: utf-8 -*-
#
# Load i18n for TracPortalPlugin.
#
# (c) 2013 Internet Initiative Japan Inc.
# Created on 2011/02/01
# @author: yosinobu@iij.ad.jp

from pkg_resources import resource_filename

from trac.core import *
from trac.util.translation import domain_functions
from trac.env import IEnvironmentSetupParticipant

_, tag_, N_, add_domain = domain_functions('tracportal',
                                           ('_', 'tag_', 'N_', 'add_domain'))

class I18NLoader(Component):
    implements(IEnvironmentSetupParticipant)

    def __init__(self):
        # i18n
        add_domain(self.env.path, resource_filename('tracportal', 'locale'))
        self.log.info("Added domain 'tracportal' -> %s",
                      resource_filename('tracportal', 'locale'))

    def environment_created(self):
        pass

    def environment_needs_upgrade(self, db):
        return False

    def upgrade_environment(self, db):
        return False
