#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python setup script for TracPortalPlugin
#
# (C) 2013 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2013/06/27
# @author: yosinobu@iij.ad.jp

from setuptools import setup, find_packages

extra = {}
try:
    import babel
    extractors = [
        ('**.py', 'python', None),
        ('**/templates/**.html', 'genshi', None),
        ('**/templates/**.txt', 'genshi',
         {'template_class': 'genshi.template:TextTemplate'}),
    ]
    extra['message_extractors'] = {
        'tracportal': extractors,
        'tracportalopt': extractors,
    }
    from trac.dist import get_l10n_js_cmdclass
    extra['cmdclass'] = get_l10n_js_cmdclass()

except ImportError:
    pass

setup(
    name = 'TracPortalPlugin',
    version = '0.1.0',
    author = 'yosinobu',
    author_email = 'yosinobu@iij.ad.jp',
    description = 'Provide trac portal pages for multiple projects.',
    url='http://www.iij.ad.jp',
    license = 'MIT',
    packages = find_packages(exclude=['*.tests']),
    package_data = {
        '': ['templates/*'],
        'tracportal': ['htdocs/*.*', 'htdocs/README', 'htdocs/js/*.*',
                       'htdocs/js/messages/*.*', 'htdocs/css/*.*',
                       'htdocs/guide/*', 'locale/*/LC_MESSAGES/*.mo',
                       'htdocs/css/smoothness/*.css', 'htdocs/css/smoothness/images/*.*'],
        'tracportalopt': []
    },
    zip_safe = True,
    entry_points = """
        [trac.plugins]
        tracportal.api = tracportal.api
        tracportal.core = tracportal.core
        tracportal.project_list.api = tracportal.project_list.api
        tracportal.project_list.web_ui = tracportal.project_list.web_ui
        tracportal.upgrade = tracportal.upgrade
        tracportal.search.web_ui = tracportal.search.web_ui
        tracportal.dashboard.web_ui = tracportal.dashboard.web_ui
        tracportal.dashboard.web_api = tracportal.dashboard.web_api
        tracportal.project.web_ui = tracportal.project.web_ui
        tracportal.i18n = tracportal.i18n
        tracportalopt.project.notification = tracportalopt.project.notification
        tracportalopt.project.ticket_notify = tracportalopt.project.ticket_notify
    """,
    requires = ['Trac', 'TracXMLRPC'],
    **extra
)
