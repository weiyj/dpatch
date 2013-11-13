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

from patchengine import PatchEngine
from dpatch.lib.common.const import CHECK_RELEASE_TYPE

class CheckReleaseEngine(PatchEngine):
    def __init__(self, repo, logger = None, build = None):
        PatchEngine.__init__(self, repo, logger, build)
        self._content = []
        self._nochk_files = ["include/generated/utsrelease.h"]
        self._included = False
        self._used = False
        self._type = CHECK_RELEASE_TYPE

    def name(self):
        return 'check release'

    def _modify_source_file(self):
        newctx = []
        if self._included == True:
            for line in self._content:
                if re.match(r"\s*#\s*include\s*<generated/utsrelease.h>", line):
                    continue
                newctx.append(line)
            self._write_to_file(''.join(newctx))
        else:
            self.warning("need to add #include <generated/utsrelease.h> to %s" % self._fname)

    def _should_patch(self):
        if self._nochk_files.count(self._fname):
            return False

        # reset global values
        self._included = False
        self._used = False
        self._content = self._read_from_file()

        # fast path
        sctx = ''.join(self._content)
        if sctx.find("<generated/utsrelease.h>") == -1 and sctx.find("UTS_RELEASE") == -1:
            return False

        incomment = False
        for line in self._content:
            if incomment == True:
                #print line
                if line.find("*/") != -1:
                    line = re.sub("^.*\*/", "", line)
                    incomment = False
                    #print "end comment **********"
                else:
                    continue

            # remove comments like '/* XXXX */'
            # comments linke /* XXX// */
            if line.find("/*") != -1:
                #print line
                # comments linke 'xxxx //*test = aaa'
                if line.find("//") != -1 and line.find("//") < line.find("/*"):
                    #print "special comment: %s" % line
                    line = re.sub("//.*$", "", line)
                # string not comment start like "rm -f %s/*\n"
                #line = re.sub("\"[^\"]+\"", "", line)
                # how to handle?
                line = re.sub("/\*.*\*/", "", line)
                if line.find("/*") != -1:
                    #print "start comment ********"
                    incomment = True
                    continue

            # remove comments like 'XXXX // XXXX'
            if line.find("//") != -1:
                line = re.sub("//.*$", "", line)

            if re.match(r"\s*#\s*include\s*<generated/utsrelease.h>", line):
                self._included = True
            elif re.search(r"\W+UTS_RELEASE", line) != None:
                #if self._included == False:
                #    print line
                self._used = True

            if self._included == True and self._used == True:
                return False

        if incomment == True:
            self.warning("something wrong when check comments: %s" % self._fname)

        #if self._included != self._used:
        if self._included == True and self._used == False:
            return True

        return False
