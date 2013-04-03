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

class CocciFormater(object):
    def __init__(self, title, desc, content, options, fixed, exceptinfo = []):
        self._title = title
        self._desc = desc
        self._content= content
        self._options = options
        self._fixed = fixed
        self._exceptinfo = exceptinfo

    def format(self):
        spctx = '/// %s\n' % self._title
        spctx += '///\n'
        if len(self._options) > 0:
            spctx += '/// Options: %s\n' % self._options
            spctx += '///\n'
        if len(self._fixed) > 0:
            spctx += '/// Fixed: %s\n' % self._fixed
            spctx += '///\n'
        for einfo in self._exceptinfo:
            if einfo.has_key('reason'):
                spctx += '/// Except File: %s : %s\n' %  (einfo['file'], einfo['reason'])
            else:
                spctx += '/// Except File: %s\n' % einfo['file']
        if len(self._exceptinfo) > 0:
            spctx += '///\n'
        for line in self._desc.split('\n'):
            spctx += '/// %s\n' %  line
        spctx += '///\n'
        spctx += self._content
        return spctx

    def save(self, path):
        spctx = self.format()
        try:
            cocci = open(path, "w")
            cocci.write(spctx)
            cocci.close()
        except:
            pass
