# -*- coding: utf-8 -*-
# (C) 2011 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2012/08/07
# @author: yosinobu@iij.ad.jp

from setuptools import setup, find_packages

setup(
    name = 'TracSyncAuthPlugin',
    version = '0.0.1',
    author = 'yosinobu',
    author_email = 'yosinobu@iij.ad.jp',
    description = 'プロジェクト間でBasic認証の認証状況を同期するプラグイン',
    url='http://www.iij.ad.jp',
    license = 'NEW BSD',
    packages = find_packages(exclude=['*.tests']),
    package_data = {
        '': ['templates/*'],
        'syncauth': [],
    },
    zip_safe = True,
    entry_points = {
        'trac.plugins': [
            'syncauth.auth = syncauth.auth',
        ]
    },
)
