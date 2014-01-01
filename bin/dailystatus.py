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
import subprocess

from time import localtime, strftime
from datetime import datetime

from django.db.models import Q

from dpatch.models import GitRepo, GitTag, Type, Patch, Report, ScanLog
from dpatch.lib.engine.manager import patch_engine_list, report_engine_list
from dpatch.lib.common.logger import MyLogger
from dpatch.lib.common.gittree import GitTree
from dpatch.lib.db.sysconfig import read_config
from dpatch.lib.common.status import *
from dpatch.lib.common.flags import TYPE_SCAN_NEXT_ONLY

def update_patch_status(patch, status):
    patch.status = status
    patch.save()
    if patch.mergered != 0:
        mpatch = Patch.objects.filter(id = patch.mergered)
        if len(mpatch) != 0:
            mpatch[0].status = status
            mpatch[0].save()

def update_report_status(report, status):
    report.status = status
    report.save()
    if report.mergered != 0:
        mreport = Report.objects.filter(id = report.mergered)
        if len(mreport) != 0:
            mreport[0].status = status
            mreport[0].save()

def execute_shell_full(args):
    if isinstance(args, basestring):
        shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
    else:
        shelllog = subprocess.Popen(args, stdout=subprocess.PIPE)
    shellOut = shelllog.communicate()[0]

    lines = shellOut.split("\n")

    return lines

def may_reject_cleanup(filename):
    # http://marc.info/?l=linux-ide&m=134988347418046&w=2
    # From David S. Miller <davem@davemloft.net>
    # Sorry, the IDE device layer is in deep freeze state, no simplifications,
    # no cleanups.
    # I'll accept changes that address kernel-wide API adjustments, but that's
    # it.
    if filename.find('drivers/ide/') == 0 or filename == 'include/linux/ide.h':
        return True

    return False

def main(args):
    for patch in Patch.objects.filter(commit = '', status = STATUS_ACCEPTED):
        if not os.path.exists(os.path.join(patch.tag.repo.dirname(), patch.file)):
            continue
        ptitle = re.sub('Subject: \[PATCH[^\]]*]', '', patch.title).strip()
        ptitle = re.sub('^.*:', '', ptitle).strip()
        if len(ptitle) > 2:
            ptitle = ptitle[1:]
        cmds = 'cd %s; git log --author="%s" --pretty="format:%%H|%%s" %s' % (patch.tag.repo.dirname(), patch.tag.repo.user, patch.file)
        for line in execute_shell_full(cmds)[::-1]:
            if line.find('|') == -1:
                continue
            rtitle = line.split('|')[1]
            if line.upper().find(ptitle.upper()) == -1 and ptitle.upper().find(rtitle.upper()) == -1:
                continue
            commit = line.split('|')[0]
            if Patch.objects.filter(commit = commit).count() != 0:
                continue
            patch.commit = commit
            patch.save()
            break

    for report in Report.objects.filter(commit = '', status = STATUS_ACCEPTED):
        if not os.path.exists(os.path.join(patch.tag.repo.dirname(), patch.file)):
            continue
        ptitle = re.sub('Subject: \[PATCH[^\]]*]', '', report.title).strip()
        ptitle = re.sub('^.*:', '', ptitle).strip()
        if len(ptitle) > 2:
            ptitle = ptitle[1:]
        cmds = 'cd %s; git log --author="%s" --pretty="format:%%H|%%s" %s' % (report.tag.repo.dirname(), report.tag.repo.user, report.file)
        for line in execute_shell_full(cmds)[::-1]:
            if line.find(ptitle) == -1:
                continue
            commit = line.split('|')[0]
            if Report.objects.filter(commit = commit).count() != 0:
                continue
            report.commit = commit
            report.save()
            break

    stablerepo = None
    for repo in GitRepo.objects.filter(status = True):
        if stablerepo is None:
            stablerepo = repo
        git = GitTree(repo.name, repo.dirname(), repo.url, repo.commit, repo.stable)
        if git.is_linux_next() == True and git.get_commit() == git.get_stable():
            continue
        logger = MyLogger()
        logs = ScanLog(reponame = repo.name, tagname = '-',
                       starttime = strftime("%Y-%m-%d %H:%M:%S", localtime()),
                       desc = 'Processing, please wait...')
        logs.save()

        for tag in GitTag.objects.filter(repo = repo):
            ptotal = Patch.objects.filter(tag = tag, mergered = 0).count()
            rtotal = Report.objects.filter(tag = tag, mergered = 0).count()
            if ptotal != tag.total:
                tag.total = ptotal
                tag.save()
            if rtotal != tag.rptotal:
                tag.rptotal = rtotal
                tag.save()
            if tag.running is True:
                tag.running = False
                tag.save()

        pcount = {'total': 0, 'removed': 0, 'fixed': 0, 'applied': 0, 'stable': 0}
        for dot in patch_engine_list():
            test = dot(repo.dirname(), logger.logger, repo.builddir())
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

                logger.info('Starting update type %d' % test.get_type())

                if repo.name == 'linux-next.git':
                    patchs = Patch.objects.filter(Q(type = rtype), Q(status = STATUS_NEW) | Q(status = STATUS_SENT))
                else:
                    patchs = Patch.objects.filter(Q(tag__repo = repo), Q(type = rtype),
                                                  Q(status = STATUS_NEW) | Q(status = STATUS_SENT))

                for patch in patchs:
                    if not patch.mglist is None and len(patch.mglist) != 0:
                        continue
                    test.set_filename(patch.file)
                    pcount['total'] += 1
                    print "check for %s\n" % patch.filename()
                    if may_reject_cleanup(patch.file):
                        update_patch_status(patch, STATUS_REJECTED)
                        logger.logger.info('rejected patch %d' % patch.id)
                        continue

                    if not os.path.exists(test._get_file_path()):
                        update_patch_status(patch, STATUS_REMOVED)
                        pcount['removed'] += 1
                        logger.logger.info('removed patch %d' % patch.id)
                        continue

                    should_patch = test.should_patch()
                    if test.has_error():
                        continue
                    if should_patch == False:
                        if patch.status == STATUS_NEW:
                            if patch.mergered != 0:
                                mpatch = Patch.objects.filter(id = patch.mergered)
                                if len(mpatch) != 0:
                                    if mpatch[0].status == STATUS_SENT:
                                        update_patch_status(patch, STATUS_ACCEPTED)
                                        pcount['applied'] += 1
                                        logger.logger.info('applied patch %d' % patch.id)
                                    else:
                                        update_patch_status(patch, STATUS_FIXED)
                                        pcount['fixed'] += 1
                                        logger.logger.info('fixed patch %d' % patch.id)
                                else:
                                    update_patch_status(patch, STATUS_FIXED)
                                    pcount['fixed'] += 1
                                    logger.logger.info('fixed patch %d' % patch.id)
                            else:
                                update_patch_status(patch, STATUS_FIXED)
                                pcount['fixed'] += 1
                                logger.logger.info('fixed patch %d' % patch.id)
                        elif patch.status == STATUS_SENT:
                            update_patch_status(patch, STATUS_ACCEPTED)
                            pcount['applied'] += 1
                            logger.logger.info('applied patch %d' % patch.id)
                    elif repo.name == 'linux-next.git' and patch.mergered == 0 and patch.status == STATUS_NEW:
                        if patch.tag.repo.name == 'linux-next.git':
                            continue
                        if rtype.type != 1:
                            continue
                        if (rtype.flags & TYPE_SCAN_NEXT_ONLY) != 0:
                            continue
                        tststable = dot(stablerepo.dirname(), logger.logger, stablerepo.builddir())
                        tststable.set_token(test.get_token())
                        tststable.set_filename(patch.file)
                        if not os.path.exists(tststable._get_file_path()):
                            continue
                        if tststable.should_patch() and not tststable.has_error():
                            ntag = GitTag.objects.filter(repo__id = stablerepo.id).order_by("-id")
                            if len(ntag) == 0:
                                continue
                            oldtag = patch.tag
                            newtag = ntag[0]
                            oldtag.total = oldtag.total - 1
                            newtag.total = newtag.total + 1
                            oldtag.save()
                            newtag.save()
                            patch.tag = newtag
                            patch.save()
                            pcount['stable'] += 1
                            logger.logger.info('stable patch %d' % patch.id)

                logger.info('End scan type %d' % test.get_type())
                logs.logs = logger.getlog()
                logs.save()
                test.next_token()

        for dot in report_engine_list():
            test = dot(repo.dirname(), logger.logger, repo.builddir())
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

                logger.info('Starting update type %d' % test.get_type())
                if repo.name == 'linux-next.git':
                    patchs = Report.objects.filter(Q(type = rtype), Q(status = STATUS_NEW) | Q(status = STATUS_PATCHED) | Q(status = STATUS_SENT))
                else:
                    patchs = Report.objects.filter(Q(tag__repo = repo), Q(type = rtype),
                                                   Q(status = STATUS_NEW) | Q(status = STATUS_PATCHED) | Q(status = STATUS_SENT))
                for patch in patchs:
                    if not patch.mglist is None and len(patch.mglist) != 0:
                        continue

                    if may_reject_cleanup(patch.file):
                        update_patch_status(patch, STATUS_REJECTED)
                        logger.logger.info('rejected patch %d' % patch.id)
                        continue
    
                    if not os.path.exists(os.path.join(repo.dirname(), patch.file)):
                        update_report_status(patch, STATUS_REMOVED)
                        pcount['removed'] += 1
                        logger.logger.info('removed patch %d' % patch.id)
                        continue

                    test.set_filename(patch.file)
                    should_report = test.should_report()
                    if test.has_error():
                        continue
                    if should_report == False:
                        if patch.status == STATUS_NEW:
                            update_report_status(patch, STATUS_FIXED)
                            pcount['fixed'] += 1
                            logger.logger.info('fixed patch %d' % patch.id)
                        elif patch.status == STATUS_SENT:
                            update_report_status(patch, STATUS_ACCEPTED)
                            pcount['applied'] += 1
                            logger.logger.info('applied patch %d' % patch.id)
                        elif patch.status == STATUS_PATCHED:
                            if patch.mergered != 0:
                                mpatch = Report.objects.filter(id = patch.mergered)
                                if len(mpatch) != 0:
                                    if mpatch[0].status == STATUS_SENT:
                                        update_report_status(patch, STATUS_ACCEPTED)
                                        pcount['applied'] += 1
                                        logger.logger.info('applied patch %d' % patch.id)
                                    else:
                                        update_report_status(patch, STATUS_FIXED)
                                        pcount['fixed'] += 1
                                        logger.logger.info('fixed patch %d' % patch.id)
                                else:
                                    update_report_status(patch, STATUS_FIXED)
                                    pcount['fixed'] += 1
                                    logger.logger.info('fixed patch %d' % patch.id)
                            else:
                                update_report_status(patch, STATUS_FIXED)
                                pcount['fixed'] += 1
                                logger.logger.info('fixed patch %d' % patch.id)
                    elif repo.name == 'linux-next.git' and patch.mergered == 0:
                        if patch.tag.repo.name == 'linux-next.git':
                            continue
                        if rtype.type != 1:
                            continue
                        if (rtype.flags & TYPE_SCAN_NEXT_ONLY) != 0:
                            continue
                        if not patch.status in [STATUS_NEW, STATUS_PATCHED]:
                            continue
                        tststable = dot(stablerepo.dirname(), logger.logger, stablerepo.builddir())
                        tststable.set_token(test.get_token())
                        tststable.set_filename(patch.file)
                        if not os.path.exists(tststable._get_file_path()):
                            continue
                        if tststable.should_report() and not tststable.has_error():
                            ntag = GitTag.objects.filter(repo__id = stablerepo.id).order_by("-id")
                            if len(ntag) == 0:
                                continue
                            oldtag = patch.tag
                            newtag = ntag[0]
                            oldtag.rptotal = oldtag.rptotal - 1
                            newtag.rptotal = newtag.rptotal + 1
                            oldtag.save()
                            newtag.save()
                            patch.tag = newtag
                            patch.save()
                            pcount['stable'] += 1
                            logger.logger.info('stable patch %d' % patch.id)
    
                logger.info('End scan type %d' % rtype.id)
                logs.logs = logger.getlog()
                logs.save()
                test.next_token()

        logs.desc = 'total checked: %d, removed: %d, fixed: %d, applied: %d, stable: %s' % (
                        pcount['total'], pcount['removed'], pcount['fixed'], pcount['applied'], pcount['stable'])
        logs.endtime = strftime("%Y-%m-%d %H:%M:%S", localtime())
        logs.logs = logger.getlog()
        logs.save()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
