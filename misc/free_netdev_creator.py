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
import sys
import tempfile

from misc import is_source_file, _execute_shell

COCCI = '@e@\n\
identifier nm, dev;\n\
@@\n\
struct nm {\n\
...\n\
struct net_device *dev;\n\
...\n\
};\n\
\n\
@script:python depends on e@\n\
nm << e.nm;\n\
dev << e.dev;\n\
@@\n\
\n\
print "struct %s|%s" % (nm, dev)\n'

def main(args):
    kdir = '/var/lib/dpatch/repo/linux-next'

    fname = tempfile.mktemp('.cocci')
    fp = open(fname, "w")
    fp.write(COCCI)
    fp.close()

    print '\
/// use free_netdev() instead of kfree() in {{function}}\n\
///\n\
/// Freeing netdev without free_netdev() leads to net, tx leaks.\n\
/// And it may lead to dereferencing freed pointer.\n\
///\n'

    stypes = []
    sargs = '/usr/bin/spatch -I %s -timeout 60 -very_quiet -sp_file %s %s' % (
                        os.path.join(kdir, 'include'), fname, kdir)
    for line in _execute_shell(sargs):
        if line.find('|') == -1:
            continue
        a = line.split('|')
        # skip sub field
        if a[1].find('->') != -1:
            continue
        if stypes.count(a) != 0:
            continue
        stypes.append(a)
        print '@@\n\
%s *x;\n\
@@\n\
- kfree(x->%s);\n\
+ free_netdev(x->%s);\n' % (a[0], a[1].split('\n')[0], a[1].split('\n')[0])

    os.unlink(fname)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
