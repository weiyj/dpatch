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

import simplejson

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from dpatch.models import ScanLog, Event

def get_request_paramter(request, key):
    if request.GET.has_key(key):
        return request.GET[key]
    elif request.POST.has_key(key):
        return request.POST[key]
    return None

def logs(request):
    context = RequestContext(request)
    return render_to_response("event/logs.html", context)

def log_data(request):
    page = int(get_request_paramter(request, 'page'))
    rp = int(get_request_paramter(request, 'rp'))

    rstart = rp * (page - 1)
    rend = rp * page

    logs = {'page': 1, 'total': 0, 'rows': [] }
    logcnt = ScanLog.objects.all().count()

    for log in ScanLog.objects.all().order_by("-id")[rstart:rend]:
        if len(log.logs) != 0:
            action = '<a href="#" class="detail" id="%s"/>Detail</a>' % log.id
        else:
            action = '-'
        logs['rows'].append({
            'id': log.id,
            'cell': {
                'id': log.id,
                'repo': log.reponame,
                'tag': log.tagname,
                'start': log.starttime,
                'end': log.endtime,
                'desc': log.desc,
                'actions': action,
        }}) # comment

    logs['page'] = page
    logs['total'] = logcnt

    return HttpResponse(simplejson.dumps(logs))

def events(request):
    context = RequestContext(request)
    return render_to_response("event/events.html", context)

def event_data(request):
    page = int(get_request_paramter(request, 'page'))
    rp = int(get_request_paramter(request, 'rp'))

    rstart = rp * (page - 1)
    rend = rp * page

    events = {'page': 1, 'total': 0, 'rows': [] }
    eventcnt = Event.objects.all().count()

    for event in Event.objects.all().order_by("-id")[rstart:rend]:
        if event.status == False:
            status = '<font color=red>FAILED</font>'
        else:
            status = '<font color=green>SUCCEED</font>'
        events['rows'].append({
            'id': event.id,
            'cell': {
                'id': event.id,
                'date': event.date.strftime("%Y-%m-%d %H:%M:%S"),
                'user': event.user,
                'event': event.event,
                'status': status,
        }}) # comment

    events['page'] = page
    events['total'] = eventcnt

    return HttpResponse(simplejson.dumps(events))

def log_detail(request, log_id):
    logs = ScanLog.objects.filter(id = log_id)
    context = RequestContext(request)
    context['logs'] = logs
    return render_to_response("event/logdetail.html", context)

@login_required
def event_delete(request):
    eids = get_request_paramter(request, 'ids')
    if eids is None:
        return HttpResponse('DELETE ERROR: no event id specified')

    ids = eids.split(',')
    events = []
    for i in ids:
        event = Event.objects.filter(id = i)
        if len(event) == 0:
            return HttpResponse('DELETE ERROR: event %s does not exists' % i)
        events.append(event[0])

    for event in events:
        event.delete()

    return HttpResponse('DELETE SUCCEED: event ids [%s]' % eids)

@login_required
def log_delete(request):
    lids = get_request_paramter(request, 'ids')
    if lids is None:
        return HttpResponse('DELETE ERROR: no log id specified')

    ids = lids.split(',')
    logs = []
    for i in ids:
        log = ScanLog.objects.filter(id = i)
        if len(log) == 0:
            return HttpResponse('DELETE ERROR: log %s does not exists' % i)
        logs.append(log[0])

    for log in logs:
        log.delete()

    return HttpResponse('DELETE SUCCEED: log ids [%s]' % lids)
