#!/usr/bin/python
#
# Dailypatch - automated kernel patch create engine
# Copyright (C) 2012 Wei Yongjun <weiyj.lk@gmail.com>
#
# This file is part of the Dailypatch package.
#
# Dailypatch is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Dailypatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Patchwork; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import sys
from dpatch.models import GitRepo, Status, Type

def main(args):
    repo = GitRepo(url = 'git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git',
                   name = 'linux.git', user = 'Wei Yongjun', email = 'weiyj.lk@gmail.com',
                   status = True, delta = False)
    repo.save()

    repo = GitRepo(url = 'git://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git',
                   name = 'linux-next.git', user = 'Wei Yongjun', email = 'weiyj.lk@gmail.com',
                   status = True, delta = True)
    repo.save()

    for s in ['New', 'Sent', 'Mergered', 'Accepted', 'Rejected', 'Fixed', 'Removed', 'Patched']:
        status = Status(name = s)
        status.save()

    types = [{'id': 1000,
              'name': 'checkversion',
              'title': 'remove unused including <linux/version.h>',
              'desc': 'Remove including <linux/version.h> that don\'t need it.'},
             {'id': 1100,
              'name': 'checkrelease',
              'title': 'remove unused including <generated/utsrelease.h>',
              'desc': 'Remove including <generated/utsrelease.h> that don\'t need it.'},
             {'id': 2000,
              'name': 'checkinclude',
              'title': 'remove duplicated include from {{file}}',
              'desc': 'Remove duplicated include.'},]

    for t in types:
        stype = Type(id = t['id'], name = t['name'], ptitle = t['title'], pdesc = t['desc'])
        stype.save()

if __name__ == '__main__':
    sys.exit(main(sys.argv))