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
import subprocess

from patchengine import PatchEngine
from dpatch.lib.common.const import CHECK_SPARSE_TYPE

class CheckSparseEngine(PatchEngine):
    def __init__(self, repo, logger = None, build = None):
        PatchEngine.__init__(self, repo, logger, build)
        self._content = []
        self._nochk_dirs = ["arch", "Documentation", "include", "tools", "usr", "samples", "scripts"]
        self._included = False
        self._used = False
        self._type = CHECK_SPARSE_TYPE

    def _execute_shell(self, args):
        if isinstance(args, basestring):
            shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            shelllog = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        shellOut = shelllog.communicate()[0]

        if shelllog.returncode != 0 and len(shellOut) > 0:
            self.warning(shellOut)

        lines = shellOut.split("\n")
        lines = lines[0:-1]

        return lines

    def name(self):
        return 'check sparse'

    def _get_patch_title(self):
        _cnt = {'total': 0, 'symbol': 0, 'null': 0, 'unused': 0}
        title = 'fix sparse warning'
        for line in self._diff:
            if self._is_symbol_not_declared(line): 
                _cnt['symbol'] += 1
                _cnt['total'] += 1
            elif self._is_plain_integer_as_null(line):
                _cnt['null'] += 1
                _cnt['total'] += 1

        if _cnt['symbol'] == _cnt['total']:
            title = 'fix sparse non static symbol warning'
        elif _cnt['unused'] == _cnt['total']:
            title = 'fix sparse unused variable warning'
        elif _cnt['null'] == _cnt['total']:
            title = 'fix sparse NULL pointer warning'
        # fix sparse endianness warnings

        if _cnt['total'] > 1:
            title += 's'

        return title

    def _get_patch_description(self):
        if len(self._diff) > 1:
            _desc = 'Fixes the following sparse warnings:\n'
        else:
            _desc = 'Fixes the following sparse warning:\n'

        for line in self._diff:
            if len(line) > 80:
                a = line.split(':')
                if len(a) > 4:
                    _desc += '\n' + ':'.join(a[:4])
                    _desc += ':\n' + ':'.join(a[4:])
                else:
                    _desc += '\n' + line
            else:
                _desc += '\n' + line

        #_desc += '\n'

        return _desc

    def _is_symbol_function(self, nr, sym):
        _lines = self._execute_shell("sed -n '%s,1p' %s" % (nr, self._get_build_path()))
        _line = _lines[0]
        if re.search('%s\s*\(' % sym, _line):
            return True
        return False

    def _make_line_static(self, _nr):
        self._execute_shell("sed -i '%ds/^/static /' %s" % (_nr, self._get_build_path()))
        return True

    def _is_symbol_not_declared(self, line):
        if re.search("symbol '\w+' was not declared", line):
            return True
        return False

    def _fix_symbol_not_declared(self, line):
        a = line.split(':')
        if len(a) < 5:
            return
        _nr = int(a[1])
        _sym = re.sub("'", "", a[-1].strip().split(' ')[1])
        if _nr < 5:
            return
        _inlines = self._execute_shell("sed -n '%d,%dp' %s" % (_nr -4, _nr + 4, self._get_build_path()))
        if re.search('%s\s*\(' % _sym, _inlines[4]):
            _fix = False
            for i in [0, 1, 2, 3]:
                line = _inlines[3 - i]
                if not re.search("\w+\s*$", line):
                    self._make_line_static(_nr - i)
                    _fix = True
                    break
            if _fix is False:
                self._make_line_static(_nr)
        else:
            self._make_line_static(_nr)

    def _is_plain_integer_as_null(self, line):
        if re.search("Using plain integer as NULL pointer", line):
            return True
        return False

    def _fix_plain_integer_as_null(self, line):
        a = line.split(':')
        if len(a) < 5:
            return False
        # E == 0 => !E sed -e '%ss/\([^ \(]*\)\s*==\s*0\([^0-9]\)/!\\1\\2/'
        self._execute_shell("sed -i '%ss/\([^ \(]*\)\s*==\s*0\([^0-9]\)/!\\1\\2/' %s" % (a[1], self._get_build_path()))
        # E != 0 => E sed -e '%ss/\s*!=\s*0\([^0-9]\)/\\1/'
        self._execute_shell("sed -i '%ss/\s*!=\s*0\([^0-9]\)/\\1/' %s" % (a[1], self._get_build_path()))
        # return 0 => return NULL
        self._execute_shell("sed -i '%ss/\([^0-9]\)0\([^0-9]\)/\\1NULL\\2/' %s" % (a[1], self._get_build_path()))
        return True

    def _modify_source_file(self):
        for line in self._diff:
            if self._is_symbol_not_declared(line): 
                self._fix_symbol_not_declared(line)
            elif self._is_plain_integer_as_null(line):
                self._fix_plain_integer_as_null(line)

    def _is_buildable(self):
        _objname = re.sub("\.c$", ".o", self._fname)
        if not os.path.exists(self._build):
            return False
        if not os.path.exists(os.path.join(self._build, 'vmlinux')):
            return True
        if not os.path.exists(os.path.join(self._build, _objname)):
            return False
        return True

    def _should_patch(self):
        if re.search(r"\.c$", self._fname) == None:
            return False
        if self._build is None:
            return False
        if not self._is_buildable():
            return False
        for _skip in self._nochk_dirs:
            if self._fname.find(_skip) == 0:
                return False
        _objname = re.sub("\.c$", ".o", self._fname)
        args = "cd %s; make C=2 %s | grep '^%s'" % (self._build, _objname, self._fname)
        self._diff = self._execute_shell(args)
        for line in self._diff:
            if self._is_symbol_not_declared(line): 
                return True
            elif self._is_plain_integer_as_null(line):
                return True
        return False

    def _revert_soure_file(self):
        os.system("cd %s ; git diff %s | patch -p1 -R > /dev/null" % (self._build, self._fname))

    def _get_diff(self):
        diff = subprocess.Popen("cd %s ; LC_ALL=en_US git diff --patch-with-stat %s" % (self._build, self._fname),
                                shell=True, stdout=subprocess.PIPE)
        diffOut = diff.communicate()[0]
        return diffOut

if __name__ == "__main__":
    repo = "/pub/scm/build/linux-test"
    files = ['drivers/usb/gadget/zero.h', 'net/netfilter/nft_lookup.c']

    count = 0
    for sfile in files:
        detector = CheckSparseEngine("/pub/scm/build/linux-next", None, repo)
        detector.set_filename(sfile)
        #print detector._guess_mail_list()
        if detector.should_patch():
            count += 1
            print detector.get_patch_title()
            print detector.get_patch_description()
            print detector.get_patch()

    print "patch files: %d" % count
