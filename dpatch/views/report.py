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

import os
import tarfile
import subprocess

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.utils import simplejson
from django.utils import html
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from dpatch.models import GitRepo, GitTag, Report, Status, Event
from dpatch.patchformat import PatchFormat 

def get_request_paramter(request, key, default=None):
    if request.GET.has_key(key):
        return request.GET[key]
    elif request.POST.has_key(key):
        return request.POST[key]
    return default

def logevent(event, status = False):
    evt = Event(event = event, status = status)
    evt.save()

def report_list(request, tag_name):
    context = RequestContext(request)
    context['tag'] = tag_name
    context['repo'] = get_request_paramter(request, 'repo', '1')
    return render_to_response("report/reportlist.html", context)

def report_list_data(request, tag_name):
    page = int(get_request_paramter(request, 'page'))
    rp = int(get_request_paramter(request, 'rp'))

    rid = int(get_request_paramter(request, 'repo', '1'))

    reports = {'page': 1, 'total': 0, 'rows': [] }
    repo = GitRepo.objects.filter(id = rid)
    if (len(repo) == 0):
        return render_to_response(simplejson.dumps(reports))

    rtag = GitTag.objects.filter(name = tag_name, repo = repo[0])
    if (len(rtag) == 0):
        return render_to_response(simplejson.dumps(reports))

    for report in Report.objects.filter(tag = rtag[0], mergered = 0):
        action = ''
        if report.status.name == 'New':
            action += '<a href="#" class="detail" id="%s">Log</a>' % report.id
            if request.user.is_authenticated():
                action += '<a href="#" class="fix" id="%s">Fix</a>' % report.id
        if report.status.name == 'Patched':
            if request.user.is_authenticated():
                action += '<a href="#" class="fix" id="%s">Fix</a>' % report.id
            action += '<a href="#" class="patch" id="%s">Patch</a>' % report.id
            if request.user.is_authenticated():
                action += '<a href="#" class="send" id="%s">Send</a>' % report.id

        reports['rows'].append({
            'id': report.id,
            'cell': {
                'id': report.id,
                'file': report.file,
                'title': html.escape(report.title),
                'date': report.date.strftime("%Y-%m-%d"),
                'type': report.type.name,
                'status': report.status.name,
                'action': action,
        }}) # comment

    if rp * page > len(reports['rows']):
        end = len(reports['rows'])
    else:
        end = rp * page
    start = rp * (page - 1)
    reports['page'] = page
    reports['total'] = len(reports['rows'])
    reports['rows'] = reports['rows'][start:end]

    return HttpResponse(simplejson.dumps(reports))

@login_required
def report_delete(request):
    pids = get_request_paramter(request, 'ids')
    if pids is None:
        return HttpResponse('DELETE ERROR: no report id specified')

    ids = pids.split(',')
    reports = []
    for i in ids:
        report = Report.objects.filter(id = i)
        if len(report) == 0:
            logevent("DELETE: report [%s], ERROR: report %s does not exists" % (pids, i))
            return HttpResponse('DELETE ERROR: report %s does not exists' % i)
        reports.append(report[0])

    for report in reports:
        tag = report.tag
        report.delete()

        tag.rptotal -= 1
        tag.save()

    logevent("DELETE: report [%s], SUCCEED" % pids, True)
    return HttpResponse('DELETE SUCCEED: report ids [%s]' % pids)

def report_detail(request, report_id):
    report = Report.objects.filter(id = report_id)
    return render_to_response("report/reportdetail.html", {'report': report[0]})

def report_patch(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    context = RequestContext(request)
    context['report'] = report
    return render_to_response("report/reportpatch.html", context)

def _get_diff_and_revert(repo, fname):
    diff = subprocess.Popen("cd %s ; LC_ALL=en_US git diff --patch-with-stat %s" % (repo, fname),
                            shell=True, stdout=subprocess.PIPE)
    diffOut = diff.communicate()[0]
    os.system("cd %s ; git diff %s | patch -p1 -R > /dev/null" % (repo, fname))
    return diffOut

@login_required
@csrf_exempt
def report_fix(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if request.method == "POST":
        src = get_request_paramter(request, 'src', '')

        if len(src) == 0:
            return HttpResponse('FIX: report, ERROR: no source specified')

        sfile = report.sourcefile()
        if not os.path.exists(sfile) or not os.path.isfile(sfile):
            return HttpResponse('FIX: report, ERROR: %s does not exists' % sfile)

        try:
            rtype = report.type
            repo = report.tag.repo

            srcfile = open(sfile, "w")
            src = srcfile.write(src)
            srcfile.close()
            diff = _get_diff_and_revert(repo.dirname(), report.file)

            patched = Status.objects.filter(name = 'Patched')[0]

            user = report.username()
            email = report.email()
            formater = PatchFormat(repo.dirname(), sfile, user, email,
                                   rtype.ptitle, rtype.pdesc, diff)
            report.content = formater.format_patch()
            report.title = formater.format_title()
            report.desc = rtype.pdesc
            report.emails = formater.get_mail_list()
            report.diff = diff
            report.status = patched
            report.save()
            return HttpResponse('FIX: report %d, SUCCEED' % report.id, True)
        except:
            return HttpResponse('FIX: report, ERROR: write file error')
    else:
        context = RequestContext(request)
        sfile = report.sourcefile()
        src = ''
        if os.path.exists(sfile) and os.path.isfile(sfile):
            srcfile = open(sfile, "r")
            src = srcfile.read()
            srcfile.close()
        context['report'] = report
        context['src'] = src
        return render_to_response("report/reportfix.html", context)

@login_required
def report_export(request):
    pids = get_request_paramter(request, 'ids')
    if pids is None:
        return HttpResponse('EXPORT ERROR: no report id specified')

    files = []
    idx = 1
    for pid in pids.split(','):
        report = Report.objects.filter(id = pid)
        if len(report) == 0:
            logevent("EXPORT: patch [%s], ERROR: id %s does not exists" % (pids, pid))
            return HttpResponse('EXPORT ERROR: id %s does not exists' % pid)

        if report[0].content is None or len(report[0].content) == 0:
            continue

        try:
            fname = os.path.join(report[0].dirname(), report[0].filename(idx))
            cocci = open(fname, "w")
            cocci.write(report[0].content)
            cocci.close()
            files.append(fname)
            idx = idx + 1
        except:
            pass

    response = HttpResponse(mimetype='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename=rpatchset.tar.gz'
    archive = tarfile.open(fileobj=response, mode='w:gz')

    for fname in files:
        if os.path.exists(fname):
            archive.add(fname, arcname = os.path.basename(fname))

    archive.close()

    for fname in files:
        if os.path.exists(fname):
            os.unlink(fname)

    return response

@login_required
def report_export_all(request, tag_name):
    rid = int(get_request_paramter(request, 'repo', '1'))

    repo = GitRepo.objects.filter(id = rid)
    if (len(repo) == 0):
        return render_to_response("repo id not specified")

    rtag = GitTag.objects.filter(name = tag_name, repo = repo[0])
    if (len(rtag) == 0):
        return render_to_response("tag id not specified")

    files = []
    idx = 1
    for report in Report.objects.filter(tag = rtag[0], mergered = 0).order_by("date"):
        if report.content is None or len(report.content) == 0:
            continue
        try:
            fname = os.path.join(report.dirname(), report.filename(idx))
            cocci = open(fname, "w")
            cocci.write(report.content)
            cocci.close()
            files.append(fname)
            idx = idx + 1
        except:
            pass

    response = HttpResponse(mimetype='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename=rpatchset.tar.gz'
    archive = tarfile.open(fileobj=response, mode='w:gz')

    for fname in files:
        if os.path.exists(fname):
            archive.add(fname, arcname = os.path.basename(fname))

    archive.close()

    for fname in files:
        if os.path.exists(fname):
            os.unlink(fname)

    return response
