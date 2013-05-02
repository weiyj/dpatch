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
import datetime

from time import localtime, strftime

from dpatch.models import GitRepo, GitTag, GitCommit, ScanLog, Type, ExceptFile, Patch
from dpatch.lib.common.logger import MyLogger
from dpatch.lib.common.gittree import GitTree
from dpatch.lib.engine.manager import patch_engine_list
from dpatch.lib.common.utils import is_source_file
from dpatch.lib.common.patchformater import PatchFormater
from dpatch.lib.common.flags import TYPE_SCAN_NEXT_ONLY, TYPE_CHANGE_DATE_CHECK
from dpatch.lib.db.sysconfig import read_config
from dpatch.lib.common.status import *

def check_patch(repo, git, rtag, flists, commit):
    count = 0
    scaninfo = []

    logs = ScanLog(reponame = repo.name, tagname = rtag.name,
                   starttime = strftime("%Y-%m-%d %H:%M:%S", localtime()),
                   desc = 'Processing, please wait...')
    logs.save()
    logger = MyLogger()
    logger.logger.info('%d Files changed' % len(flists))
    #logger.logger.info('=' * 40)
    #logger.logger.info('%s' % '\n'.join(flists))
    #logger.logger.info('=' * 40)

    sche_weekend_only = read_config('patch.schedule.weekend.only', True)
    sche_weekend_limit = read_config('patch.schedule.weekend.limit', 600)
    sche_weekend_delta = read_config('patch.schedule.weekend.delta', 90)
    sche_obsolete_skip = read_config('patch.schedule.obsolete.skip', False)
    weekday = datetime.datetime.now().weekday()

    for dot in patch_engine_list():
        scount = 0
        test = dot(repo.dirname(), logger.logger)
        for i in range(test.tokens()):
            rtype = None
            try:
                rtype = Type.objects.filter(id = test.get_type())[0]
            except:
                test.next_token()
                continue

            if rtype.status == False:
                test.next_token()
                continue

            if (rtype.flags & TYPE_SCAN_NEXT_ONLY) != 0 and not git.is_linux_next():
                test.next_token()
                continue

            if rtype.type == 0 and sche_weekend_only is True and len(flists) > sche_weekend_limit and weekday < 5:
                # if we does not have a patch for this cleanup type in
                # sche_weekend_limit days, schedule scan only on weekend
                stime = datetime.datetime.now() - datetime.timedelta(days=sche_weekend_delta)
                if Patch.objects.filter(type = rtype, date__gte=stime).count() == 0:
                    test.next_token()
                    logger.info('Delay scan type %d to weekend' % test.get_type())
                    continue

            cmts = GitCommit.objects.filter(repo = repo, type = rtype)
            if len(cmts) == 0:
                cmt = GitCommit(repo = repo, type = rtype)
                cmt.save()
            else:
                cmt = cmts[0]

            if repo.delta == False:
                oldcommit = cmt.commit
                if oldcommit != repo.commit:
                    if git.is_linux_next():
                        oldcommit = git.get_stable()
                    rflists = git.get_changelist(oldcommit, commit, None, True)
                else:
                    rflists = flists
            else:
                rflists = flists

            logger.info('Starting scan type %d, total %d files' % (test.get_type(), len(rflists)))

            exceptfiles = []
            for fn in ExceptFile.objects.filter(type = rtype):
                exceptfiles.append(fn.file)

            pcount = 0
            for sfile in rflists:
                if not is_source_file(sfile):
                    continue

                if exceptfiles.count(sfile) != 0:
                    logger.logger.info('skip except file %s, type %d' % (sfile, rtype.id))
                    continue

                # treat patch marked with Rejected as except file
                if Patch.objects.filter(file = sfile, type = rtype, status = STATUS_REJECTED).count() > 0:
                    continue

                patchs = Patch.objects.filter(file = sfile, type = rtype)
                rpatchs = []
                for p in patchs:
                    if not p.status in [STATUS_NEW, STATUS_SENT, STATUS_MARKED]:
                        continue
                    rpatchs.append(p)

                test.set_filename(sfile)
                # source file maybe removed
                if not os.path.exists(test._get_file_path()):
                    for p in rpatchs:
                        p.status = STATUS_REMOVED
                        p.save()
                    continue

                # if the same file has a patch for this type, ignore it
                # because the last patch does not accepted
                should_patch = test.should_patch()
                if len(rpatchs) != 0 and should_patch == False:
                    for p in rpatchs:
                        if p.status == STATUS_SENT:
                            p.status = STATUS_ACCEPTED
                        elif p.mergered != 0:
                            mpatch = Patch.objects.filter(id = p.mergered)
                            if len(mpatch) != 0:
                                if mpatch[0].status == STATUS_SENT:
                                    mpatch[0].status = STATUS_ACCEPTED
                                    p.status = STATUS_ACCEPTED
                                else:
                                    mpatch[0].status = STATUS_FIXED
                                    p.status = STATUS_FIXED
                                mpatch[0].save()
                            else:
                                p.status = STATUS_FIXED
                        else:
                            p.status = STATUS_FIXED
                        p.save()

                if should_patch == True and len(rpatchs) == 0:
                    text = test.get_patch()

                    if (rtype.flags & TYPE_CHANGE_DATE_CHECK) == TYPE_CHANGE_DATE_CHECK:
                        if git.is_change_obsoleted(sfile, text) is True:
                            continue
                    elif rtype.type == 0 and sche_obsolete_skip is True:
                        if git.is_change_obsoleted(sfile, text) is True:
                            continue

                    patch = Patch(tag = rtag, file = sfile, type = rtype, 
                                  status = STATUS_NEW, diff = text)
                    patch.save()

                    # format patch and cache to patch
                    user = patch.username()
                    email = patch.email()
                    formater = PatchFormater(repo.dirname(), sfile, user, email,
                                             rtype.ptitle, rtype.pdesc, text)
                    patch.content = formater.format_patch()
                    patch.title = formater.format_title()
                    patch.desc = formater.format_desc()
                    patch.emails = formater.get_mail_list()
                    patch.module = formater.get_module()
                    patch.save()

                    scount += 1
                    pcount += 1

            cmt.commit = commit
            cmt.save()

            logger.info('End scan type %d, patch %d' % (test.get_type(), pcount))
            logs.logs = logger.getlog()
            logs.save()
            test.next_token()

        count += scount
        scaninfo.append("%s: %d" % (test.name(), scount))

    scaninfo.append("total: %d" % (count))
    logs.desc = ', '.join(scaninfo)
    logs.endtime = strftime("%Y-%m-%d %H:%M:%S", localtime())
    logs.logs = logger.getlog()
    logs.save()

    return count

def main(args):
    for repo in GitRepo.objects.all():
        # repo is disabled
        if repo.status == False:
            continue

        git = GitTree(repo.name, repo.dirname(), repo.url, repo.commit, repo.stable)
        otag = git.get_tag()
        if git.check_update() == False and repo.delta == True:
            rtags = GitTag.objects.filter(repo = repo, name = otag)
            if len(rtags) > 0:
                rtag = rtags[0]
                rtag.flist = ''
                rtag.save()
            continue

        # the tag name after git pull
        ntag = git.get_tag()
        if otag is None:
            otag = ntag

        if git.is_linux_next() == True:
            tag = ntag
        else:
            tag = otag
        if tag != ntag:
            # we got a new tag, just scan from last commit to otag
            # as common, new tag is the last commit, so does not need
            # to scan twice
            commit = git.get_commit_by_tag(ntag)
        else:
            commit = git.get_commit()

        # if delta scan is enbled, skip the first time since we git clone
        # the tree, treat there is no file change
        if repo.delta == True:
            if repo.commit is None or len(repo.commit) == 0:
                repo.commit = commit
                repo.save()
                continue

            # no file change
            if repo.commit == commit:
                continue

        # file change list from last update
        flists = git.get_changelist(repo.commit, commit, repo.update) 

        tags = GitTag.objects.filter(repo = repo, name = tag)
        rtag = None
        if tags.count() == 0:
            rtag = GitTag(repo = repo, name = tag, flist = ','.join(flists), total = 0)
            rtag.save()
        else:
            rtag = tags[0]

        if rtag.running == True:
            continue

        rtag.running = True
        rtag.save()

        print "Check for repo %s" % os.path.basename(repo.url)
        pcount = check_patch(repo, git, rtag, flists, commit)

        rtag.total += pcount
        rtag.flist = ','.join(flists)
        rtag.running = False
        rtag.save()

        repo.commit = commit
        if git.is_linux_next():
            repo.stable = git.get_stable()
        repo.update = git.get_update_date()
        repo.save()
        print "Total patch %d" % pcount

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
