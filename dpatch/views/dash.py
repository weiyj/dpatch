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

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils import simplejson

from dpatch.models import GitTag, Type, Patch, ScanLog

def patch_by_type(request):
    ptypes = {}

    for rtype in Type.objects.all():
        cnt = Patch.objects.filter(type = rtype).count()
        ptypes[rtype.name] = cnt

    return HttpResponse(simplejson.dumps(ptypes))

def patch_by_tag(request):
    tags = []
    for tag in GitTag.objects.all():
        tags.append({'name': tag.name, 'total': tag.total})

    return HttpResponse(simplejson.dumps(tags))

def patch_by_daily(request):
    dcounts = []
    for log in ScanLog.objects.all():
        dt = log.starttime
        desc = log.desc
        if desc.find('total:') != -1:
            dcounts.append({'date': dt, 'count': desc.split(':')[-1]})
    return HttpResponse(simplejson.dumps(dcounts))
