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

STATUS_NEW = 1
STATUS_SENT = 2
STATUS_MERGED = 3
STATUS_ACCEPTED = 4
STATUS_REJECTED = 5
STATUS_FIXED = 6
STATUS_REMOVED = 7
STATUS_PATCHED = 8
STATUS_IGNORED = 9
STATUS_OBSOLETED = 10
STATUS_MARKED = 11

BUILD_TBD = 0
BUILD_PASS = 1
BUILD_FAIL = 2
BUILD_SKIP = 3
BUILD_WARN = 4

def status_name(status): 
    if status == STATUS_NEW:
        return 'NEW'
    elif status == STATUS_FIXED:
        return 'FIXED'
    elif status == STATUS_REMOVED:
        return 'REMOVED'
    elif status == STATUS_SENT:
        return 'SENT'
    elif status == STATUS_MERGED:
        return 'MERGED'
    elif status == STATUS_ACCEPTED:
        return 'APPLIED'
    elif status == STATUS_REJECTED:
        return 'REJECTED'
    elif status == STATUS_IGNORED:
        return 'IGNORED'
    elif status == STATUS_OBSOLETED:
        return 'OBSOLETED'
    elif status == STATUS_PATCHED:
        return 'PATCHED'
    elif status == STATUS_MARKED:
        return 'MARKED'
    else:
        return 'UNKNOWN'

def status_name_list(rlist = []):
    rstatus = []
    for i in range(STATUS_MARKED):
        if (i + 1) in rlist:
            continue
        rstatus.append("%s=%s" %(status_name(i+1), i+1))
    return '|'.join(rstatus)

def status_name_html(status):
    name = status_name(status)
    if name == 'NEW':
        return '<FONT COLOR="#000000">%s</FONT>' % name
    elif name in ['FIXED', 'REMOVED', 'MERGED', 'IGNORED', 'OBSOLETED', 'UNKNOWN']:
        return '<FONT COLOR="#AAAAAA">%s</FONT>' % name
    elif name in ['PATCHED']:
        return '<FONT COLOR="#0000AA">PATCHED</FONT>'
    elif name in ['SENT']:
        return '<FONT COLOR="#0000FF">SENT</FONT>'
    elif name in ['APPLIED']:
        return '<FONT COLOR="#00FF00">APPLIED</FONT>'
    else:
        return '<FONT COLOR="#FF0000">%s</FONT>' % name

def build_name(build):
    if build == BUILD_TBD:
        return 'TBD'
    elif build == BUILD_PASS:
        return 'PASS'
    elif build == BUILD_FAIL:
        return 'FAIL'
    elif build == BUILD_SKIP:
        return 'SKIP'
    elif build == BUILD_WARN:
        return 'WARN'
    else:
        return 'UNKONWN'

def build_name_list():
    return 'PASS=1|FAIL=2|WARN=4|SKIP=3|TBD=0'

def build_name_html(build):
    if build == 0:
        return 'TBD'
    elif build == BUILD_PASS:
        return '<FONT COLOR="#0000FF">PASS</FONT>'
    elif build == BUILD_FAIL:
        return '<FONT COLOR="#FF0000">FAIL</FONT>'
    elif build == BUILD_WARN:
        return '<FONT COLOR="#00FF00">WARN</FONT>'
    elif build == BUILD_SKIP:
        return '<FONT COLOR="#AAAAAA">SKIP</FONT>'
    else:
        return '<FONT COLOR="#FF0000">UNKONWN</FONT>'
