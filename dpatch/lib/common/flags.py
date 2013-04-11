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

TYPE_SCAN_NEXT_ONLY = 0x01
TYPE_CHANGE_DATE_CHECK = 0x02
TYPE_BUILD_SPARSE_CHECK = 0x04

def flags_name(flags):
    flagname = []
    if (flags & TYPE_SCAN_NEXT_ONLY) == TYPE_SCAN_NEXT_ONLY:
        flagname.append('NEXT_ONLY')
    if (flags & TYPE_CHANGE_DATE_CHECK) == TYPE_CHANGE_DATE_CHECK:
        flagname.append('DATE_CHK')
    if (flags & TYPE_BUILD_SPARSE_CHECK) == TYPE_BUILD_SPARSE_CHECK:
        flagname.append('SPARSE_CHK')
    if len(flagname):
        return '|'.join(flagname)
    return '-'
