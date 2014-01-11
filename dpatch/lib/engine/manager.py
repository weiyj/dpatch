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

from checkversion import CheckVersionEngine
from checkinclude import CheckIncludeEngine
from checkrelease import CheckReleaseEngine
from checksparse import CheckSparseEngine
from checkcoccinelle import CheckCocciPatchEngine, CheckCocciReportEngine

def patch_engine_list():
    return [CheckVersionEngine, CheckReleaseEngine, CheckIncludeEngine, CheckSparseEngine, CheckCocciPatchEngine]

def report_engine_list():
    return [CheckCocciReportEngine]