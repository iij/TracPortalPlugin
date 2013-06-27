# -*- coding: utf-8 -*-
#
# Created on 2011/02/14
# @author: yosinobu@iij.ad.jp
#
import unittest
from tracportalopt.api import LdapProjectListProvider, expand_actions
from trac.test import EnvironmentStub


class Test(unittest.TestCase):

    def setUp(self):
        self.env = EnvironmentStub()

    def test_expand_actions1(self):
        actions = expand_actions(['WIKI_VIEW'])
        self.assertEqual(['WIKI_ADMIN', 'TRAC_ADMIN', 'WIKI_VIEW'], actions)

    def test_expand_actions2(self):
        actions = expand_actions(['WIKI_ADMIN'])
        self.assertEqual(['WIKI_ADMIN', 'TRAC_ADMIN'], actions)

    def test_expand_actions3(self):
        actions = expand_actions(['TRAC_ADMIN'])
        self.assertEqual(['TRAC_ADMIN'], actions)

    def test_generate_ldap_filter_some_actions(self):
        self.env.config.set('ldap', 'basedn', 'dc=iij,dc=ad,dc=jp')
        provider = LdapProjectListProvider(self.env)
        fstr = provider.generate_filter(['WIKI_VIEW', 'TICKET_VIEW'], ['anonymous'])
        self.assertEqual('(|(&(&(|(tracperm=*:WIKI_ADMIN)(tracperm=*:TRAC_ADMIN)(tracperm=*:WIKI_VIEW))'
                         '(|(tracperm=*:TICKET_ADMIN)(tracperm=*:TRAC_ADMIN)(tracperm=*:TICKET_VIEW)))(uid=anonymous))'
                         '(&(&(|(tracperm=*:WIKI_ADMIN)(tracperm=*:TRAC_ADMIN)(tracperm=*:WIKI_VIEW))'
                         '(|(tracperm=*:TICKET_ADMIN)(tracperm=*:TRAC_ADMIN)(tracperm=*:TICKET_VIEW)))'
                         '(member=uid=anonymous,ou=tracusers,dc=iij,dc=ad,dc=jp)))', fstr)

    def test_generate_ldap_filter_some_users(self):
        self.env.config.set('ldap', 'basedn', 'dc=iij,dc=ad,dc=jp')
        provider = LdapProjectListProvider(self.env)
        fstr = provider.generate_filter(['TRAC_ADMIN'], ['anonymous', 'authenticated'])
        self.assertEqual('(|(&(tracperm=*:TRAC_ADMIN)(|(uid=anonymous)(uid=authenticated)))'
                         '(&(tracperm=*:TRAC_ADMIN)'
                         '(|(member=uid=anonymous,ou=tracusers,dc=iij,dc=ad,dc=jp)'
                         '(member=uid=authenticated,ou=tracusers,dc=iij,dc=ad,dc=jp))))', fstr)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGenerateLdapFilter']
    unittest.main()
