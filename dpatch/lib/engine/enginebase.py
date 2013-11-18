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

class EngineBase(object):
    def __init__(self, repo, logger = None, build = None):
        self._repo = repo
        self._build = build
        self._fname = None
        self._type = 0
        self._token = 0
        self._logger = logger

    def name(self):
        return 'undefined engine'

    def set_filename(self, fname):
        self._fname = fname.replace('./', '')

    def tokens(self):
        return 1

    def next_token(self):
        self._token += 1
        return self._token

    def set_token(self, token):
        self._token = token

    def has_error(self):
        return False

    def get_type(self):
        return self._type

    def error(self, msg):
        if self._logger != None:
            self._logger.error(msg)

    def info(self, msg):
        if self._logger != None:
            self._logger.info(msg)

    def debug(self, msg):
        if self._logger != None:
            self._logger.info(msg)

    def warning(self, msg):
        if self._logger != None:
            self._logger.info(msg)

    def _get_file_path(self):
        return os.path.join(self._repo, self._fname)

    def _get_build_path(self):
        return os.path.join(self._build, self._fname)

    def _read_from_file(self):
        if not os.path.exists(self._get_file_path()):
            return []

        srcfile = open(self._get_file_path(), "r")
        lines = srcfile.readlines()
        srcfile.close()
        return lines

    def _write_to_file(self, content):
        srcfile = open(self._get_file_path(), "w")
        srcfile.write(content)
        srcfile.close()
