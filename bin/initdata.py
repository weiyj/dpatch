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

import sys
from dpatch.models import GitRepo, Type

def main(args):
    if GitRepo.objects.filter(name = 'linux.git').count() == 0:
        repo = GitRepo(url = 'git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git',
                       name = 'linux.git', user = 'Wei Yongjun', email = 'yongjun_wei@trendmicro.com.cn',
                       status = True, delta = False, build = True)
        repo.save()

    if GitRepo.objects.filter(name = 'linux-next.git').count() == 0:
        repo = GitRepo(url = 'git://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git',
                       name = 'linux-next.git', user = 'Wei Yongjun', email = 'yongjun_wei@trendmicro.com.cn',
                       status = True)
        repo.save()

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
        if Type.objects.filter(name = t['name']).count() > 0:
            continue
        stype = Type(id = t['id'], name = t['name'], ptitle = t['title'], pdesc = t['desc'], status = False)
        stype.save()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
