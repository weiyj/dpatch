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
from time import gmtime, strftime

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

def html_report_status(name):
    if name == 'New':
        return '<FONT COLOR="#000000">NEW</FONT>'
    elif name == 'Fixed':
        return '<FONT COLOR="#AAAAAA">FIXED</FONT>'
    elif name == 'Removed':
        return '<FONT COLOR="#AAAAAA">REMOVED</FONT>'
    elif name == 'Patched':
        return '<FONT COLOR="#0000AA">PATCHED</FONT>'
    elif name == 'Sent':
        return '<FONT COLOR="#0000FF">SENT</FONT>'
    elif name == 'Merged':
        return '<FONT COLOR="#AAAAAA">MERGED</FONT>'
    elif name == 'Accepted':
        return '<FONT COLOR="#00FF00">APPLIED</FONT>'
    else:
        return name

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
        elif report.status.name == 'Patched':
            if request.user.is_authenticated():
                action += '<a href="#" class="fix" id="%s">Fix</a>' % report.id
            action += '<a href="#" class="patch" id="%s">Patch</a>' % report.id
            if request.user.is_authenticated():
                action += '<a href="#" class="edit" id="%s">Edit</a>' % report.id
                if report.build in [1, 3, 4]:
                    action += '<a href="#" class="send" id="%s">Send</a>' % report.id
        elif report.status.name == 'Sent':
            if request.user.is_authenticated():
                action += '<a href="#" class="fix" id="%s">Fix</a>' % report.id
            action += '<a href="#" class="patch" id="%s">Patch</a>' % report.id
            if request.user.is_authenticated():
                action += '<a href="#" class="edit" id="%s">Edit</a>' % report.id

        if report.build == 0:
            build = 'TBD'
        elif report.build == 1:
            build = '<a href="#" class="build" id="%s"><FONT COLOR="#0000FF">PASS</FONT></a>' % report.id
        elif report.build == 2:
            build = '<a href="#" class="build" id="%s"><FONT COLOR="#FF0000">FAIL</FONT></a>' % report.id
        elif report.build == 4:
            build = '<a href="#" class="build" id="%s"><FONT COLOR="#00FF00">WARN</FONT></a>' % report.id
        elif report.build == 3:
            build = '<FONT COLOR="#AAAAAA">SKIP</FONT>'

        reports['rows'].append({
            'id': report.id,
            'cell': {
                'id': report.id,
                'file': report.file,
                'title': html.escape(report.title),
                'date': report.date.strftime("%Y-%m-%d"),
                'type': report.type.name,
                'status': html_report_status(report.status.name),
                'build': build,
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

def report_format(patch):
    user = patch.username()
    email = patch.email()

    ctx = "Content-Type: text/plain; charset=ISO-8859-1\n"
    ctx += "Content-Transfer-Encoding: 7bit\n"
    ctx += "From: %s <%s>\n" % (user, email)
    ctx += "Date: %s\n" % strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
    ctx += "Subject: %s\n" % patch.title
    ctx += "%s\n" % patch.emails
    #ctx += "From: %s <%s>\n\n" % (user, email)
    ctx += "%s\n\n" % patch.desc
    ctx += "Signed-off-by: %s <%s>\n" % (user, email)
    ctx += "---\n"
    ctx += "%s\n" % patch.diff

    return ctx

@login_required
@csrf_exempt
def report_edit(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if request.method == "POST":
        title = get_request_paramter(request, 'title')
        desc = get_request_paramter(request, 'desc')
        emails = get_request_paramter(request, 'emails')
        diff = get_request_paramter(request, 'diff')
    
        if title is None or len(title) == 0:
            logevent("EDIT: report %s, ERROR: no title specified" % report_id)
            return HttpResponse('EDIT ERROR: no report title specified')
    
        if desc is None or len(desc) == 0:
            logevent("EDIT: report %s, ERROR: no desc specified" % report_id)
            return HttpResponse('EDIT ERROR: no report desc specified')
    
        if emails is None or len(emails) == 0:
            logevent("EDIT: report %s, ERROR: no emails specified" % report_id)
            return HttpResponse('EDIT ERROR: no report emails specified')
    
        if diff is None or len(diff) == 0:
            logevent("EDIT: report %s, ERROR: no diff specified" % report_id)
            return HttpResponse('EDIT ERROR: no report diff specified')

        report.title = title
        report.desc = desc
        report.emails = emails
        if report.diff != diff:
            report.build = 0
            report.diff = diff
            report.status = Status.objects.get(name = 'Patched')

        report.content = report_format(report)
        report.save()

        logevent("EDIT: report %s, SUCCEED" % report_id, True)
        return HttpResponse('EDIT SUCCEED')
    else:
        context = RequestContext(request)
        context['report'] = report
        return render_to_response("report/reportedit.html", context)

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

            patched = Status.objects.get(name = 'Patched')

            user = report.username()
            email = report.email()
            formater = PatchFormat(repo.dirname(), report.file, user, email,
                                   rtype.ptitle, rtype.pdesc, diff)
            report.content = formater.format_patch()
            if report.title is None or len(report.title) == 0:
                report.title = formater.format_title()
            if report.desc is None or len(report.desc) == 0:
                report.desc = rtype.pdesc
            report.emails = formater.get_mail_list()
            report.diff = diff
            report.build = 0
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
    response['Content-Disposition'] = 'attachment; filename=rpatchset-%s.tar.gz' % strftime("%Y%m%d%H%M%S", gmtime())
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
    response['Content-Disposition'] = 'attachment; filename=rpatchset-all-%s.tar.gz' % strftime("%Y%m%d%H%M%S", gmtime())
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
def report_sendwizard(request, report_id):
    context = RequestContext(request)
    context['reportid'] = report_id
    return render_to_response("report/sendwizard.html", context)

def execute_shell(args):
    if isinstance(args, basestring):
        shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    else:
        shelllog = subprocess.Popen(args, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    shellOut = shelllog.communicate()[0]

    return shelllog.returncode, shellOut

def getgitconfig(name):
    args = 'git config %s' % name
    shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
    shellOut = shelllog.communicate()[0]

    lines = shellOut.split("\n")

    return lines[0]

@csrf_exempt
def report_sendwizard_step(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    step = get_request_paramter(request, 'step_number', 1)

    if step == '1':
        ctx = '<pre>%s</pre>' % html.escape(report.content)
    elif step == '2':
        rdir = report.tag.repo.dirname()
        cpatch = os.path.join(rdir, 'scripts/checkpatch.pl')

        temp = report.fullpath()
        cfg = open(temp, "w")
        cfg.write(report.content)
        cfg.close()

        #os.system('/usr/bin/dos2unix %s' % patch.fullpath())

        ret1, chkpatch = execute_shell('%s %s' % (cpatch, temp))
        chkpatch = chkpatch.replace(temp, 'patch')
        ret2, apatch = execute_shell('cd %s && git apply --check %s' % (rdir, temp))
        if ret2 == 0:
            apatch = 'patch can be apply succeed'
        ctx = '<pre># scripts/checkpatch.pl %s\n\n%s\n# git apply --check %s\n\n%s</pre>' \
                % (temp, chkpatch, temp, apatch)
        ctx = ctx.replace(report.dirname(), '')
        if ret1 != 0 or ret2 != 0:
            ctx += '<div id="steperrors"><font color=red>Please correct above errors first!</font></div>'
    elif step == '3':
        crypt = getgitconfig('sendemail.smtpencryption')
        server = getgitconfig('sendemail.smtpserver')
        port = getgitconfig('sendemail.smtpserverport')
        user = getgitconfig('sendemail.smtpuser')
        #password = getgitconfig('sendemail.smtppass')
        mfrom = getgitconfig('sendemail.from')

        if len(crypt) == 0 or len(server) == 0 or len(port) == 0 or len(user) == 0 or len(mfrom) == 0:
            ctx = '<div id="steperrors"><font color=red>Your SMTP setting is not correctly!</font></div>'
            return HttpResponse(ctx)
            
        email = report.emails.replace('To:', '')
        email = email.replace('Cc:', '')
        email = email.replace(',', '')
        emails = email.split("\n")
        to = ''
        for addr in emails:
            if len(addr.strip()) != 0:
                to = addr.strip()
                break

        ret, drun = execute_shell('/usr/bin/git send-email --dry-run --no-thread --to=\'%s\' %s' \
                                % (to, report.fullpath()))
        drun = drun.replace(report.dirname(), '')
        if ret != 0:
            ctx = '<pre>%s</pre>' % (html.escape(drun))
            ctx += '<div id="steperrors"><font color=red>Your SMTP setting is not correctly!</font></div>'
            return HttpResponse(ctx)

        context = RequestContext(request)
        context['emails'] = emails
        context['to'] = to
        return render_to_response("patch/sendwarnning.html", context)
    elif step == '4':
        email = report.emails
        email = email.replace('To:', '')
        email = email.replace('Cc:', '')
        email = email.replace(',', '')
        emails = email.split("\n")
        to = ''
        for addr in emails:
            if len(addr.strip()) != 0:
                to = addr.strip()
                break

        ret, drun = execute_shell('/usr/bin/git send-email --quiet --no-thread --confirm=never --to=\'%s\' %s' \
                                % (to, report.fullpath()))
        drun = drun.replace(report.dirname(), '')
        if ret != 0:
            ctx = '<pre>%s</pre>' % (html.escape(drun))
            ctx += '<div id="steperrors"><font color=red>Your SMTP setting is not correctly!</font></div>'
            return HttpResponse(ctx)

        sent = Status.objects.filter(name = 'Sent')[0]
        report.status = sent
        report.save()

        ctx = '<pre>Patch has been sent succeed!</pre>'

        #if os.path.exists(patch.fullpath()):
        #    os.unlink(patch.fullpath())
    else:
        ctx = '<pre>UNKNOW step</pre>'

    return HttpResponse(ctx)

def report_build(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    return render_to_response("report/reportbuild.html", {'buildlog': report.buildlog})
