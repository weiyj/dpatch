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

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext

from dpatch.models import GitRepo, GitTag, Type, Patch, Report, ScanLog
from dpatch.lib.common.status import STATUS_ACCEPTED

import simplejson

def patch_status(request, repo_id):
    context = RequestContext(request)
    context['repo'] = repo_id
    return render_to_response("dash/dashstatus.html", context)

def patch_by_type(request, repo_id):
    ptypes = {}

    repos = GitRepo.objects.filter(id = repo_id)
    if len(repos) == 0:
        return HttpResponse(simplejson.dumps(ptypes))

    for rtype in Type.objects.all():
        cnt = Patch.objects.filter(type = rtype, tag__repo = repos[0]).count()
        if cnt != 0:
            ptypes[rtype.name] = cnt

    return HttpResponse(simplejson.dumps(ptypes))

def patch_by_tag(request, repo_id):
    tags = []

    repos = GitRepo.objects.filter(id = repo_id)
    if len(repos) == 0:
        return HttpResponse(simplejson.dumps(tags))

    for tag in GitTag.objects.filter(repo = repos[0]):
        pcnt = Patch.objects.filter(tag = tag, status = STATUS_ACCEPTED).exclude(commit = '').count()
        tags.append({'name': tag.name, 'total': tag.total, 'applied': pcnt})

    return HttpResponse(simplejson.dumps(tags))

def patch_by_daily(request, repo_id):
    dcounts = []

    repos = GitRepo.objects.filter(id = repo_id)
    if len(repos) == 0:
        return HttpResponse(simplejson.dumps(dcounts))

    for log in ScanLog.objects.filter(reponame = repos[0].name):
        dt = log.starttime
        desc = log.desc
        if desc.find('total:') != -1:
            dcounts.append({'date': dt, 'count': desc.split(':')[-1]})
    return HttpResponse(simplejson.dumps(dcounts))
