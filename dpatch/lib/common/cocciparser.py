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

import re

class CocciParser(object):
    def __init__(self, lines):
        self._lines = lines
        self._title = ''
        self._fixed = ''
        self._options = ''
        self._desc = ''
        self._efiles = []
        self._content = ''

    def parser(self):
        desc = []
        content = []
        isdesc = False
        isctx = False
        for i in range(len(self._lines)):
            if i == 0:
                self._title = self._lines[i]
                self._title = self._title.replace('///', '').strip()
                continue

            if isdesc == False and isctx == False:
                line = self._lines[i]
                if line.find('/// Options:') == 0:
                    self._options = line
                    self._options = self._options.replace('/// Options:', '').strip()
                elif line.find('/// Fixed:') == 0:
                    self._fixed = line
                    self._fixed = self._fixed.replace('/// Fixed:', '').strip()
                elif line.find('/// Except File:') == 0:
                    exceptfile = line
                    exceptfile = exceptfile.replace('/// Except File:', '').strip()
                    efileinfo = exceptfile.split(':')
                    if len(efileinfo) == 1:
                        efileinfo.append('')
                    self._efiles.append({'file': efileinfo[0].strip(), 'reason': efileinfo[1].strip()})
                else:
                    descline = line
                    descline = descline.replace('///', '').strip()
                    if len(descline) != 0:
                        desc.append(descline)
                        isdesc = True
                continue
    
            if isdesc == True:
                descline = self._lines[i]
                if descline.find('///') != -1:
                    descline = descline.replace('///', '').strip()
                    desc.append(descline)
                    continue
                else:
                    isdesc = False
                    isctx = True
    
            if isctx == False:
                continue
            content.append(self._lines[i])
    
        if len(desc[-1]) == 0:
            desc = desc[:-1]

        self._desc = '\n'.join(desc)
        self._content = ''.join(content)

    def get_title(self):
        return self._title

    def get_fixed(self):
        return self._fixed

    def get_options(self):
        return self._options

    def get_description(self):
        return self._desc

    def get_efiles(self):
        return self._efiles

    def get_content(self):
        return self._content
