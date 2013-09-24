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

import re

from django.shortcuts import render_to_response
from dpatch.models import GitRepo, GitTag
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.conf import settings
from dpatch.lib.db.sysconfig import read_config

def dashboard(request):
    context = RequestContext(request)
    context['repos'] = GitRepo.objects.all()
    return render_to_response("dashboard.html", context)

def patchstatus(request):
    if read_config('ui.main.showversion', True) is True:
        tags = []
        versions = {}
        rtag = {}
        for tag in GitTag.objects.filter(Q(total__gt=0) | Q(running=True)).order_by("-id"):
            version = re.sub('-rc\d+$', '', tag.name)
            if not versions.has_key(tag.repo.name):
                versions[tag.repo.name] = version
                rtag[tag.repo.name] = {'version': version, 'total': tag.total, 'repoid': tag.repo.id,
                                       'reponame': tag.repo.name, 'running': tag.running}
                tags.append(rtag[tag.repo.name])
            else:
                if versions[tag.repo.name] != version:
                    versions[tag.repo.name] = version
                    rtag[tag.repo.name] = {'version': version, 'total': tag.total, 'repoid': tag.repo.id,
                                           'reponame': tag.repo.name, 'running': tag.running}
                    tags.append(rtag[tag.repo.name])
                else:
                    rtag[tag.repo.name]['total'] += tag.total

        context = RequestContext(request)
        limit = read_config('ui.main.showitems', len(tags))
        if len(tags) > limit:
            context['tags'] = tags[0:limit]
        else:
            context['tags'] = tags
        return render_to_response("patch/statusbyversion.html", context)
    else:
        tags = GitTag.objects.filter(Q(total__gt=0) | Q(running=True)).order_by("-id")
        context = RequestContext(request)
        context['tags'] = tags
        return render_to_response("patchstatus.html", context)

def reportstatus(request):
    if read_config('ui.main.showversion', True) is True:
        tags = []
        versions = {}
        rtag = {}
        for tag in GitTag.objects.filter(Q(rptotal__gt=0) | Q(running=True)).order_by("-id"):
            version = re.sub('-rc\d+$', '', tag.name)
            if not versions.has_key(tag.repo.name):
                versions[tag.repo.name] = version
                rtag[tag.repo.name] = {'version': version, 'rptotal': tag.rptotal, 'repoid': tag.repo.id,
                                       'reponame': tag.repo.name, 'running': tag.running}
                tags.append(rtag[tag.repo.name])
            else:
                if versions[tag.repo.name] != version:
                    versions[tag.repo.name] = version
                    rtag[tag.repo.name] = {'version': version, 'rptotal': tag.rptotal, 'repoid': tag.repo.id,
                                           'reponame': tag.repo.name, 'running': tag.running}
                    tags.append(rtag[tag.repo.name])
                else:
                    rtag[tag.repo.name]['rptotal'] += tag.rptotal

        context = RequestContext(request)
        limit = read_config('ui.main.showitems', len(tags))
        if len(tags) > limit:
            context['tags'] = tags[0:limit]
        else:
            context['tags'] = tags
        return render_to_response("report/statusbyversion.html", context)
    else:
        tags = GitTag.objects.filter(Q(rptotal__gt=0) | Q(running=True)).order_by("-id")
        context = RequestContext(request)
        context['tags'] = tags
        return render_to_response("reportstatus.html", context)

def patchengine(request):
    context = RequestContext(request)
    return render_to_response("patchengine.html", context)

@login_required
def administration(request):
    context = RequestContext(request)
    return render_to_response("administration.html", context)

def helppage(request):
    context = RequestContext(request)
    return render_to_response("help.html", context)
