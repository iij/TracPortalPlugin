
==================
Trac Portal Plugin
==================

Provide portal pages for multiple Trac projects (Trac >= 0.12).


Installation
============

1. Please install in the same manner as any other Trac plugins::

     $ python setup.py bdist_egg
     $ cp dist/*.egg /trac/env/plugins/
     or
     $ python setup.py install

2. You will also need to enable the plugin in your (portal) environment trac.ini::

     [components]
     tracportal.* = enabled
     tracportalopt.* = enabled # (optional)

3. Need upgrade the Trac environment after installing the plugin::

     $ trac-admin /trac/env upgrade


Dependencies
============

 - Trac_ >= 0.12
 - `Trac XML-RPC Plugin`_ >= r13194

.. _Trac: http://trac.edgewall.org/wiki/TracInstall
.. _`Trac XML-RPC Plugin`: http://trac-hacks.org/wiki/XmlRpcPlugin


Configuration
=============

Example::

  [tracportal]
  ignore_projects = portal
  inherit_file = /var/www/trac/trac.ini
  notify_email_cc = xxx@example.com
  notify_email_from = yyy@example.com
  notify_email_from_name = TracPortal
  parent_base_url = http://xxx.yyy.zzz/trac/
  trac_env_parent_dir = /var/www/trac/envs

For more information, please see the wiki:TracIni.

Screenshot
==========

**Listing Projects**

  .. image:: ./screenshot/project_list.png
     :scale: 60%
     :alt: Listing Projects
     :align: left

**Dashboard**

  .. image:: screenshot/dashboard.png
     :scale: 60 %
     :alt: Dashboard
     :align: left

**Cross Search**

  .. image:: screenshot/cross_search.png
     :scale: 60 %
     :alt: Cross Search
     :align: left

**Project Creation**

  .. image:: screenshot/project_creation.png
     :scale: 60 %
     :alt: Project Creation
     :align: left

