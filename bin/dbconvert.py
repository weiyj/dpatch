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

import dpatch.lib.misc.oldmodels
import dpatch.models
import dpatch.lib.common.gittree

def main(args):
    for git in dpatch.lib.misc.oldmodels.GitRepoOld.objects.using('olddb').all():
        dname = os.path.basename(git.url).replace('.git', '')
        dpath = os.path.join('/var/lib/dpatch/repo', dname)
        tgit = dpatch.lib.common.gittree.GitTree(git.name, dpath, git.url, git.commit)
        if tgit.is_linux_next():
            stablev = tgit.get_stable()
        else:
            stablev = ''
        ngit = dpatch.models.GitRepo(id = git.id, name = git.name, url = git.url, user = git.user,
                    email = git.email, delta = git.delta, build = git.build,
                    commit = git.commit, status = git.status, stable = '')
        ngit.stable = stablev
        ngit.update = tgit.get_update_date()
        ngit.save()

    for tag in dpatch.lib.misc.oldmodels.GitTagOld.objects.using('olddb').all():
        repo = dpatch.models.GitRepo.objects.get(name = tag.repo.name)
        ntag = dpatch.models.GitTag(id = tag.id, repo = repo, name = tag.name, total = tag.total,
                                    rptotal = tag.rptotal, flist = tag.flist)
        ntag.save()

    for cocci in dpatch.lib.misc.oldmodels.CocciEngineOld.objects.using('olddb').all():
        ncocci = dpatch.models.CocciPatchEngine(id = cocci.id, file = cocci.file,
                                                options = cocci.options, fixed = cocci.fixed,
                                                content = cocci.content)
        ncocci.save()

    for cocci in dpatch.lib.misc.oldmodels.CocciReportOld.objects.using('olddb').all():
        ncocci = dpatch.models.CocciReportEngine(id = cocci.id, file = cocci.file,
                                                options = cocci.options, content = cocci.content)
        ncocci.save()

    for rtype in dpatch.lib.misc.oldmodels.TypeOld.objects.using('olddb').all():
        ntype = dpatch.models.Type(id = rtype.id, name = rtype.name, ptitle = rtype.ptitle,
                                   pdesc = rtype.pdesc, commit = rtype.commit, user = rtype.user,
                                   email = rtype.email, status = rtype.status)
        ntype.save()

    for commit in dpatch.lib.misc.oldmodels.GitCommitOld.objects.using('olddb').all():
        repo = dpatch.models.GitRepo.objects.get(id = commit.repo.id)
        rtype = dpatch.models.Type.objects.get(id = commit.type.id)
        ncommit = dpatch.models.GitCommit(id = commit.id, repo = repo, type = rtype,
                                          commit = commit.commit)
        ncommit.save()

    for efile in dpatch.lib.misc.oldmodels.ExceptFileOld.objects.using('olddb').all():
        rtype = dpatch.models.Type.objects.get(id = efile.type.id)
        nefile = dpatch.models.ExceptFile(id = efile.id, type = rtype, file = efile.file,
                                          reason = efile.reason)
        nefile.save()

    for report in dpatch.lib.misc.oldmodels.ReportOld.objects.using('olddb').all():
        tag = dpatch.models.GitTag.objects.get(id = report.tag.id)
        rtype = dpatch.models.Type.objects.get(id = report.type.id)
        nreport = dpatch.models.Report(id = report.id, tag = tag, type = rtype,
                                     status = report.status.id, file = report.file,
                                     date = report.date, mergered = report.mergered,
                                     mglist = report.mglist, commit = report.commit,
                                     reportlog = report.reportlog, 
                                     module = '', diff = report.diff, title = report.title,
                                     desc = report.desc, emails = report.emails, comment = '',
                                     content = report.content, build = report.build,
                                     buildlog = report.buildlog)
        nreport.save()

    for patch in dpatch.lib.misc.oldmodels.PatchOld.objects.using('olddb').all():
        tag = dpatch.models.GitTag.objects.get(id = patch.tag.id)
        rtype = dpatch.models.Type.objects.get(id = patch.type.id)
        npatch = dpatch.models.Patch(id = patch.id, tag = tag, type = rtype,
                                     status = patch.status.id, file = patch.file,
                                     date = patch.date, mergered = patch.mergered,
                                     mglist = patch.mglist, commit = patch.commit,
                                     module = '', diff = patch.diff, title = patch.title,
                                     desc = patch.desc, emails = patch.emails, comment = '',
                                     content = patch.content, build = patch.build,
                                     buildlog = patch.buildlog)
        npatch.save()

    for log in dpatch.lib.misc.oldmodels.ScanLogOld.objects.using('olddb').all():
        nlog = dpatch.models.ScanLog(id = log.id, reponame = log.reponame,
                                     tagname = log.tagname,
                                     starttime = log.starttime, endtime = log.endtime,
                                     desc = log.desc, logs = log.logs)
        nlog.save()

    for event in dpatch.lib.misc.oldmodels.EventOld.objects.using('olddb').all():
        nevent = dpatch.models.Event(id = event.id, user = event.user, date = event.date,
                                     event = event.event, status = event.status)
        nevent.save()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
