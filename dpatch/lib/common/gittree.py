#!/usr/bin/python
#
# DailyPatch - Automated Linux Kernel Patch Generate Engine
# Copyright (C) 2012, 2013 Wei Yongjun <weiyj.lk@gmail.com>
#
# This file is part of the DailyPatch package.
#
# DailyPatch is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# DailyPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Patchwork; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os
import re
import datetime

from utils import execute_shell
from time import localtime, time, strftime
from utils import find_remove_lines
from dpatch.lib.db.sysconfig import read_config

class GitTree(object):
    def __init__(self, name, dpath, url, commit, stable = None):
        self._name = name
        self._dpath = dpath
        self._url = url
        self._commit = commit
        self._ncommit = None
        self._stable = stable

    def is_linux_next(self):
        if self._name == 'linux-next.git':
            return True
        else:
            return False

    def _get_remote_master(self):
        _rfile = re.sub('git://git.kernel.org', 'http://www.kernel.org', self._url)
        _rfile = _rfile + '/refs/heads/master'
        _tfile = "/tmp/%s-master--" % re.sub('\.', '-', self._name)
        execute_shell('wget -O %s %s --no-check-certificate' % (_tfile, _rfile))
        commits = execute_shell('cat %s; unlink %s' % (_tfile, _tfile))
        if len(commits) == 0:
            return None
        return commits[0]

    def update(self):
        if not os.path.exists(self._dpath):
            rpath = os.path.dirname(self._dpath)
            execute_shell('cd %s; git clone %s' % (rpath, self._url))
        else:
            if self.is_linux_next():
                rmaster = self._get_remote_master()
                if rmaster == self._commit:
                    return False
                execute_shell('cd %s; git reset --hard %s' % (self._dpath, self._stable))
            execute_shell('cd %s; git pull' % self._dpath)
        return False

    def check_update(self):
        self.update()
        commit = self.get_commit()
        if commit == self._commit:
            return False
        else:
            return True

    def get_commit(self):
        commits = execute_shell('cd %s; git log -n 1 --pretty=format:%%H%%n' % self._dpath)
        return commits[-1]

    def get_commit_by_tag(self, tag):
        commits = execute_shell('cd %s; git log -n 1 %s --pretty=format:%%H%%n' % (self._dpath, tag))
        return commits[-1]

    def get_tag(self):
        if not os.path.exists(self._dpath):
            return None
        tags = execute_shell('cd %s; git tag' % self._dpath)

        stag = tags[-1]
        if re.search(r'-rc\d+$', stag) != None:
            tag = re.sub('-rc\d+$', '', stag)
            if tags.count(tag) > 0:
                stag = tag

        for ltag in tags[::-1]:
            if re.search(r'v\d.\d\d+', ltag) != None:
                lversions = re.sub('-rc\d+$', '', ltag).split('.')
                sversions = re.sub('-rc\d+$', '', stag).split('.')
                if lversions[0] != sversions[0] or int(sversions[-1]) > int(lversions[-1]):
                    return stag
                else:
                    tag = re.sub('-rc\d+$', '', ltag)
                    if tags.count(tag) > 0:
                        ltag = tag
                    return ltag

        return stag

    def get_stable(self):
        if self._ncommit is None:
            commits = execute_shell('cd %s ; cat .git/refs/remotes/origin/stable' % self._dpath)
            self._ncommit = commits[0]
        return self._ncommit

    def _get_date_zone(self, data):
        offset = int(data[-5:])
        delta = datetime.timedelta(hours = offset / 100)
        return datetime.datetime.strptime(data[:-6], '%Y-%m-%d %H:%M:%S') - delta

    def get_update_date(self):
        dates = execute_shell('cd %s; git log -n 1 --pretty=format:%%ci%%n' % self._dpath)
        try:
            date = datetime.datetime.strptime(dates[-1], '%Y-%m-%d %H:%M:%S %z')
        except:
            date = self._get_date_zone(dates[-1])
        return date

    def get_changelist(self, scommit, ecommit, update, delta = False):
        if scommit == ecommit and len(scommit) != 0:
            return []
        dateusing = read_config('git.diff.using.datetime', False)
        if self.is_linux_next():
            if dateusing is True and delta is False:
                if not isinstance(update, datetime.datetime):
                    stime = strftime("%Y-%m-%d %H:%M:%S", localtime(time() - 2 * 24 * 60 * 60))
                else:
                    stime = update# - datetime.timedelta(days=2)
                lines = execute_shell('cd %s; git log --after="%s" --name-only --format="%%" | sort -u | grep "\w"' % (self._dpath, stime))
                return lines
            else:
                scommit = self.get_stable()
                lines = execute_shell('cd %s; git diff --name-only %s...%s' % (self._dpath, scommit, ecommit))
                return lines
        else:
            if len(scommit) == 0 or scommit is None:
                scommit = '1da177e4c3f41524e886b7f1b8a0c1fc7321cac2'
            lines = execute_shell('cd %s; git diff --name-only %s...%s' % (self._dpath, scommit, ecommit))
            return lines

    def is_change_obsoleted(self, fname, diff):
        dates = []
        days = read_config('patch.obsoleted.days', 30)
        for line in find_remove_lines(diff):
            dates = execute_shell("cd %s; git log -n 1 -S '%s' --pretty=format:%%ci%%n %s" % (self._dpath, line, fname))
            if len(dates) == 0:
                continue
            dt = datetime.datetime.strptime(' '.join(dates[0].split(' ')[:-1]), "%Y-%m-%d %H:%M:%S")
            delta = datetime.datetime.now() - dt
            if delta.days < days:
                return False
        return True
