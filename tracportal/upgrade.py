# -*- coding: utf-8 -*-
#
# Setup database for the plugin.
#
# (C) 2013 Internet Initiative Japan Inc.
# All rights reserved.
#
# Created on 2011/01/27
# @author: yosinobu@iij.ad.jp

from trac.core import *
from trac.env import IEnvironmentSetupParticipant


class SetupTracPortal(Component):

    implements(IEnvironmentSetupParticipant)

    db_tables = ('cache_projects', 'cache_projects_stats')

    # IEnvironmentSetupParticipant
    def environment_created(self):
        pass

    def environment_needs_upgrade(self, db):
        return len(self._has_tables(self.env.get_read_db())) != len(self.db_tables)

    def upgrade_environment(self, db):
        self.log.info('Creating tables of TracPortalPlugin in database...')
        has_tables = self._has_tables(self.env.get_read_db())
        if 'cache_projects' not in has_tables:
            sql = [
                """CREATE TABLE cache_projects (
                    id VARCHAR(255) primary key,
                    name VARCHAR(255),
                    url VARCHAR(255),
                    description TEXT,
                    updated_at INTEGER
                );""",
                """CREATE INDEX cache_projects_idx ON cache_projects(id, name);""",
                """CREATE TRIGGER insert_cache_projects AFTER INSERT ON cache_projects
                BEGIN
                UPDATE cache_projects SET updated_at = STRFTIME('%s', 'NOW') WHERE id = NEW.id;
                END;""",
                """CREATE TRIGGER update_cache_projects AFTER UPDATE  ON cache_projects
                BEGIN
                UPDATE cache_projects SET updated_at = STRFTIME('%s', 'NOW') WHERE id = NEW.id;
                END;"""]
            cursor = db.cursor()
            for s in sql:
                cursor.execute(s)
            db.commit()
            self.log.info('Successfully created the table "cache_projects" in database.')
        if 'cache_projects_stats' not in has_tables:
            sql = [
                """CREATE TABLE cache_projects_stats (
                    id VARCHAR(255) primary key,
                    changes INTEGER,
                    changes_month INTEGER,
                    tickets INTEGER,
                    tickets_month INTEGER,
                    tickets_closed INTEGER,
                    tickets_closed_month INTEGER,
                    updated_at INTEGER
                );""",
                """CREATE INDEX cache_projects_stats_idx ON cache_projects_stats(id);""",
                """CREATE TRIGGER insert_cache_projects_stats AFTER  INSERT ON cache_projects_stats
                BEGIN
                    UPDATE cache_projects_stats SET updated_at = STRFTIME('%s', 'NOW') WHERE id = NEW.id;
                END;""",
                """CREATE TRIGGER update_cache_projects_stats AFTER UPDATE  ON cache_projects_stats
                BEGIN
                    UPDATE cache_projects_stats SET updated_at = STRFTIME('%s', 'NOW') WHERE id = NEW.id;
                END;"""]
            cursor = db.cursor()
            for s in sql:
                cursor.execute(s)
            db.commit()
            self.log.info('Successfully created the table "cache_projects_stats" in database.')

    # Internal methods
    def _has_tables(self, db):
        has_tables = []
        cursor = db.cursor()
        for tbl in self.db_tables:
            try:
                cursor.execute('SELECT COUNT(*) FROM %s' % tbl)
                has_tables.append(tbl)
            except Exception, e:
                self.log.info(e)
                pass
        return has_tables
