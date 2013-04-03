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

from enginebase import EngineBase

class ReportEngine(EngineBase):
    def __init__(self, repo, logger = None):
        EngineBase.__init__(self, repo, logger)

    def name(self):
        return 'undefined report engine'

    def should_report(self):
        if self._fname is None:
            return False

        if not os.path.exists(self._get_file_path()):
            return False

        return self._should_report()

    def _should_report(self):
        return False

    def get_report(self):
        return []
