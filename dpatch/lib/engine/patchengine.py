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
import subprocess

from enginebase import EngineBase

class PatchEngine(EngineBase):
    def __init__(self, repo, logger = None):
        EngineBase.__init__(self, repo, logger)

    def name(self):
        return 'undefined patch engine'

    def should_patch(self):
        if self._fname is None:
            return False

        if not os.path.exists(self._get_file_path()):
            return False

        return self._should_patch()

    def get_patch(self):
        self._modify_source_file()
        patch = self._get_diff()
        self._revert_soure_file()
        if len(patch) < 2:
            self.error("can not get diff for %s : type %d" % (self._fname, self.get_type()))
        return patch

    def _get_patch_title(self):
        return "undefined patch title"

    def get_patch_title(self):
        return self._get_patch_title()

    def _get_patch_description(self):
        return "undefined patch description"

    def get_patch_description(self):
        return self._get_patch_description()

    def _get_comment(self):
        return "undefined comment"

    def _should_patch(self):
        return False

    def _modify_source_file(self):
        pass

    def _revert_soure_file(self):
        os.system("cd %s ; git diff %s | patch -p1 -R > /dev/null" % (self._repo, self._fname))

    def _get_diff(self):
        diff = subprocess.Popen("cd %s ; LC_ALL=en_US git diff --patch-with-stat %s" % (self._repo, self._fname),
                                shell=True, stdout=subprocess.PIPE)
        diffOut = diff.communicate()[0]
        return diffOut
    