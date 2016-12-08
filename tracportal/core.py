# -*- coding: utf-8 -*-
#
# User Interface Module for Trac Portal Plugin.
#
# (C) 2013 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2013/06/04
# @author: yosinobu@iij.ad.jp
import os

from trac.config import Option
from trac.core import Component, TracError

from tracportal.i18n import _


class TracPortalCore(Component):
    # class variables
    _env_key = 'TRAC_ENV_PARENT_DIR'
    parent_dir = Option('tracportal', 'trac_env_parent_dir',
                        doc=_('Prent path of trac env directories.'
                              'If not set this option, use TRAC_ENV_PARENT_DIR in python environment variables.'))
    parent_base_url = Option('tracportal', 'parent_base_url',
                             doc=_('Parent URL of base_url.'))

    @property
    def trac_env_parent_dir(self):
        parent = self.parent_dir or os.environ.get(self._env_key, '')
        if not parent:
            parent = os.path.dirname(self.env.path)
            self.log.warn('Unresolved trac_env_parent_dir. Please set a config([tracportal] trac_env_parent_dir).')
        return parent

    @property
    def trac_parent_base_url(self):
        if self.parent_base_url:
            return self.parent_base_url
        self.log.warn('Please add a config([tracportal] parent_base_url) in trac.ini.')
        base_url = self.env.base_url
        if base_url:
            env_name = os.path.basename(self.env.path.rstrip('/'))
            return base_url.replace(env_name, '').rstrip('/')
        raise TracError('Unresolved parent base_url. Please check [tracportal] configurations.')


def get_trac_env_parent_dir(env):
    return TracPortalCore(env).trac_env_parent_dir


def get_parent_base_url(env):
    return TracPortalCore(env).trac_parent_base_url
