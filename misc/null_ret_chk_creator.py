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
import sys

from misc import is_source_file, _execute_shell

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
DATAFILE = os.path.join(ROOT_DIR, 'data/NULL_RET_FUNC_LIST.txt')
SCRIPTFILE = os.path.join(ROOT_DIR, 'script/null_ret_chk_finder.cocci')

def main(args):
    kdir = '/var/lib/dpatch/repo/linux-next'

    print '/// fix return value check in {{function}}\n\
///\n\
/// In case of error, the function XXXX() returns NULL pointer\n\
/// not ERR_PTR(). The IS_ERR() test in the return value check\n\
/// should be replaced with NULL test.\n\
///\n'

    skip_list = []

    if not os.path.exists(DATAFILE):
        lines = []
        sfiles = _execute_shell("find %s -type f" % kdir)[0:-1]
        count = 0
        for sfile in sfiles:
            if not is_source_file(sfile):
                continue
            if count > 0 and count % 100 == 0:
                print 'total: %d, current: %d' % (count, len(sfiles))
            count += 1
            sargs = '/usr/bin/spatch -I %s -timeout 60 -very_quiet -sp_file %s %s' % (
                        os.path.join(kdir, 'include'), SCRIPTFILE, sfile)
            for line in _execute_shell(sargs):
                if not re.search('\w+', line):
                    continue
                if lines.count(line) != 0:
                    continue
                if line in skip_list:
                    continue
                lines.append(line)
        fp = open(DATAFILE, "w")
        fp.write('\n'.join(lines))
        fp.close()

    fp = open(DATAFILE, "r")
    lines = fp.readlines()
    fp.close()

    funcs = []
    for line in lines:
        line = line.replace('\n', '')
        if line.find('//') != -1:
            continue
        if line.find('|') != -1:
            line = line.split('|')[0]
        if line in skip_list:
            continue
        funcs.append(line)

    print '@@\n\
expression ret, E;\n\
@@\n\
ret = \(%s\)(...);\n\
... when != ret = E\n\
(\n\
- IS_ERR(ret)\n\
+ !ret\n\
|\n\
- !IS_ERR(ret)\n\
+ ret\n\
)\n' % '\|\n'.join(funcs)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))