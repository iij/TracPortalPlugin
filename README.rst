
==================
Trac Portal Plugin
==================

TracPortalPlugin is providing portal features for multiple Trac projects (Trac >= 0.12).

Features
========

- Project Index

    View a list of Trac projects which include the activity information.

- Dashboard

    View own tickets, timeline and milestone in the available projects.

- Cross Search

    Perform a search over the available projects.

- Project Creation

    Create a new Trac project.


Installation
============

1. Clone the git repository or download the zipped source::

     $ git clone https://github.com/iij/TracPortalPlugin.git
     or
     $ wget https://github.com/iij/TracPortalPlugin/archive/master.zip
     $ unzip master.zip

2. Please install in the same manner as any other Trac plugins::

     $ python setup.py bdist_egg
     $ cp dist/*.egg /trac/env/plugins/
     or
     $ python setup.py install

3. You will also need to enable the plugin in your (portal) environment trac.ini::

     [components]
     tracportal.* = enabled
     tracportalopt.* = enabled # (optional)

4. Need upgrade the Trac environment after installing the plugin::

     $ trac-admin /trac/env upgrade

5. Set the plugin's configurations

     see Configuration_

6. Grant the permission using the trac-admin tool or the General / Permissions panel in the Admin tab of web interface.

     +---------------------------------+----------------------------------------+
     | Action                          | Description                            |
     +=================================+========================================+
     | PORTAL_PROJECT_LIST_VIEW        | View the project list page.            |
     +---------------------------------+----------------------------------------+
     | PORTAL_PUBLIC_PROJECT_LIST_VIEW | View the public project list page.     |
     +---------------------------------+----------------------------------------+
     | PORTAL_DASHBOARD_VIEW           | View the dashboard page.               |
     +---------------------------------+----------------------------------------+
     | PORTAL_CROSS_SEARCH_VIEW        | View and execute cross search queries. |
     +---------------------------------+----------------------------------------+
     | PORTAL_PROJECT_CREATE           | View and create a new Trac project.    |
     +---------------------------------+----------------------------------------+


Dependencies
============

 - Trac_ >= 0.12
 - `Trac XML-RPC Plugin`_ >= r13194

.. _Trac: http://trac.edgewall.org/wiki/TracInstall
.. _`Trac XML-RPC Plugin`: http://trac-hacks.org/wiki/XmlRpcPlugin


Configuration
=============

**[tracportal]**
  +------------------------------------+---------------------------------------------------------------------------------------------------+
  |ignore_projects                     | A list of Trac environment's name that is ignore projects in the portal pages.                    |
  +------------------------------------+---------------------------------------------------------------------------------------------------+
  | inherit_file                       | Inherit config file. When create a project, set the [inherit] file option in the project config.  |
  +------------------------------------+---------------------------------------------------------------------------------------------------+
  | notify_email_cc                    | Email address(es) to always send notifications to, addresses can be seen by all recipients (Cc:). |
  +------------------------------------+---------------------------------------------------------------------------------------------------+
  | notify_email_from                  | Sender address to use in notification emails.                                                     |
  +------------------------------------+---------------------------------------------------------------------------------------------------+
  | notify_email_from_name             | Sender name to use in notification emails.                                                        |
  +------------------------------------+---------------------------------------------------------------------------------------------------+
  | notify_ticket_env                  | Trac environment for notify project creation by new ticket.                                       |
  +------------------------------------+---------------------------------------------------------------------------------------------------+
  | parent_base_url                    | Parent URL of base_ur                                                                             |
  +------------------------------------+---------------------------------------------------------------------------------------------------+
  | project_activity_assessment_period | Number of days to evaluate the project activity.                                                  |
  +------------------------------------+---------------------------------------------------------------------------------------------------+
  | project_activity_cache_ttl         | Time to live of cache(sec) for project activity.                                                  |
  +------------------------------------+---------------------------------------------------------------------------------------------------+
  | project_info_cache_ttl             | Time to live of cache(sec) for project information.                                               |
  +------------------------------------+---------------------------------------------------------------------------------------------------+
  | project_list_link_url_suffix       | Path to be appended to the project url in project list page.                                      |
  |                                    | (e.x, if need login, set "/login" value in this option.)                                          |
  +------------------------------------+---------------------------------------------------------------------------------------------------+
  | trac_env_parent_dir                | Prent path of trac env directories.                                                               |
  |                                    | If not set this option, use TRAC_ENV_PARENT_DIR in python environment variables.                  |
  +------------------------------------+---------------------------------------------------------------------------------------------------+

Example::

  [tracportal]
  ignore_projects = portal
  inherit_file = /var/www/trac/trac.ini
  notify_email_cc = xxx@example.com
  notify_email_from = yyy@example.com
  notify_email_from_name = TracPortal
  parent_base_url = http://xxx.yyy.zzz/trac/
  trac_env_parent_dir = /var/www/trac/envs

For more information, please see the wiki:TracIni

Screenshot
==========

**Project Index**

  .. image:: ./screenshot/project_list.png
     :scale: 60%
     :alt: Project Index
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

