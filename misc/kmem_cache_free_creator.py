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
type T;\n\
expression c;\n\
identifier x;\n\
@@\n\
(\n\
T x;\n\
...\n\
 x = \(kmem_cache_alloc\|kmem_cache_zalloc\|kmem_cache_alloc_node\)(c,...);\n\
|\n\
T x= \(kmem_cache_alloc\|kmem_cache_zalloc\|kmem_cache_alloc_node\)(c,...);\n\
)\n\
\n\
@script:python depends on e@\n\
T << e.T;\n\
c << e.c;\n\
@@\n\
\n\
print "%s|%s" % (T, c)\n'

def main(args):
    kdir = '/var/lib/dpatch/repo/linux-next'

    fname = tempfile.mktemp('.cocci')
    fp = open(fname, "w")
    fp.write(COCCI)
    fp.close()

    print '\
/// use kmem_cache_free() instead of kfree()\n\
///\n\
/// memory allocated by kmem_cache_alloc() should be freed using\n\
/// kmem_cache_free(), not kfree().\n\
///\n'

    stypes = []
    for sfile in _execute_shell("find %s -type f" % kdir)[0:-1]:
        if not is_source_file(sfile):
            continue
        sargs = '/usr/bin/spatch -I %s -timeout 60 -very_quiet -sp_file %s %s' % (
                        os.path.join(kdir, 'include'), fname, sfile)
        for line in _execute_shell(sargs):
            if line.find('|') == -1:
                continue
            a = line.split('|')
            # skip sub field
            if a[1].find('->') != -1:
                continue
            if stypes.count(a[0]) != 0:
                continue
            if a[0] in ['char *', 'void *', 'u32 *', 'unsigned long *', 'struct sk_buff *', 'struct urb_priv *']:
                continue
            stypes.append(a[0])
            print '@@\n\
%sx;\n\
@@\n\
- kfree(x);\n\
+ kmem_cache_free(%s, x);\n' % (a[0], a[1].split('\n')[0])

    os.unlink(fname)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
