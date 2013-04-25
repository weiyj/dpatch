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
import tarfile
import subprocess
import urllib
import urlparse
import tempfile
import cgi

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.utils import simplejson
from django.utils import html
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from time import gmtime, strftime

from dpatch.models import GitRepo, GitTag, Report, Event, Type, ExceptFile
from dpatch.lib.common.patchformater import PatchFormater
from dpatch.lib.common.patchparser import PatchParser
from dpatch.lib.common.utils import find_remove_lines
from dpatch.lib.db.filemodule import register_module_name
from dpatch.lib.engine.manager import report_engine_list
from dpatch.forms import ReportNewForm
from dpatch.lib.common.status import *

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
    rtypes = []
    for rtype in Type.objects.filter(id__gte = 10000):
        if len(rtype.name) > 30:
            rtypes.append("%s=%s" % (rtype.name[:30], rtype.id))
        else:
            rtypes.append("%s=%s" % (rtype.name, rtype.id))

    context = RequestContext(request)
    context['tag'] = tag_name
    context['repo'] = get_request_paramter(request, 'repo', '1')
    context['types'] = '|'.join(rtypes)
    context['status'] = status_name_list()
    context['build'] = build_name_list()
    return render_to_response("report/reportlist.html", context)

def report_list_version(request, tag_name):
    rtypes = []
    for rtype in Type.objects.filter(id__gte = 10000):
        if len(rtype.name) > 30:
            rtypes.append("%s=%s" % (rtype.name[:30], rtype.id))
        else:
            rtypes.append("%s=%s" % (rtype.name, rtype.id))

    rtagnames = []
    for rtag in GitTag.objects.filter(name__icontains = tag_name):
        if rtagnames.count(rtag.name) == 0:
            rtagnames.append(rtag.name)

    context = RequestContext(request)
    context['tag'] = tag_name
    context['repo'] = get_request_paramter(request, 'repo', '1')
    context['types'] = '|'.join(rtypes)
    context['status'] = status_name_list()
    context['tagnames'] = '|'.join(rtagnames)
    context['byversion'] = True
    context['build'] = build_name_list()
    return render_to_response("report/reportlist.html", context)

def reportfilter(pfilter):
    kwargs = {}

    if pfilter is None or len(pfilter) == 0:
        return kwargs

    params = urlparse.parse_qs(urllib.unquote(pfilter))
    for key in params:
        if len(params[key]) == 0:
            continue
        value = params[key][0]
        if key == 'type':
            kwargs.update({'type__id': value})
        elif key == 'status':
            kwargs.update({'status': value})
        elif key == 'file':
            kwargs.update({'file__icontains': value})
        elif key == 'build':
            kwargs.update({'build': value})
        elif key == 'tag':
            kwargs.update({'tag__name': value})
    return kwargs

def report_list_data(request, tag_name):
    page = int(get_request_paramter(request, 'page', '1'))
    rp = int(get_request_paramter(request, 'rp', '15'))

    rid = int(get_request_paramter(request, 'repo', '1'))
    rfilter = get_request_paramter(request, 'filter')
    byver = int(get_request_paramter(request, 'version', '0'))

    reports = {'page': 1, 'total': 0, 'rows': [] }
    repo = GitRepo.objects.filter(id = rid)
    if (len(repo) == 0):
        return HttpResponse(simplejson.dumps(reports))

    rstart = rp * (page - 1)
    rend = rp * page

    if byver == 0:
        rtag = GitTag.objects.filter(name = tag_name, repo = repo[0])
        if (len(rtag) == 0):
            return HttpResponse(simplejson.dumps(reports))
        kwargs = reportfilter(rfilter)
        reportcnt = Report.objects.filter(tag = rtag[0], mergered = 0, **kwargs).count()
        reportset = Report.objects.filter(tag = rtag[0], mergered = 0, **kwargs).order_by("-id")[rstart:rend]
    else:
        kwargs = reportfilter(rfilter)
        reportcnt = Report.objects.filter(tag__name__icontains = tag_name, tag__repo = repo,
                                        mergered = 0, **kwargs).count()
        reportset = Report.objects.filter(tag__name__icontains = tag_name, tag__repo = repo,
                                        mergered = 0, **kwargs).order_by("-id")[rstart:rend]

    for report in reportset:
        action = ''
        action += '<a href="#" class="detail" id="%s">Log</a>' % report.id
        if report.status == STATUS_NEW:
            if request.user.is_authenticated():
                action += '<a href="#" class="fix" id="%s">Fix</a>' % report.id
        elif report.status == STATUS_PATCHED:
            action = ''
            if request.user.is_authenticated():
                action += '<a href="#" class="fix" id="%s">Fix</a>' % report.id
            action += '<a href="#" class="patch" id="%s">Patch</a>' % report.id
            if request.user.is_authenticated():
                action += '<a href="#" class="edit" id="%s">Edit</a>' % report.id
                if report.build in [1, 3, 4]:
                    action += '<a href="#" class="send" id="%s">Send</a>' % report.id
        elif report.status == STATUS_SENT:
            if request.user.is_authenticated():
                action += '<a href="#" class="fix" id="%s">Fix</a>' % report.id
            action += '<a href="#" class="patch" id="%s">Patch</a>' % report.id
            if request.user.is_authenticated():
                action += '<a href="#" class="edit" id="%s">Edit</a>' % report.id
        elif report.status == STATUS_ACCEPTED and len(report.commit) > 0:
            url = "%s;a=commit;h=%s" % (repo[0].url, report.commit)
            url = re.sub("git://git.kernel.org/pub/scm/", "http://git.kernel.org/?p=", url)
            action = '<a href="#" class="patch" id="%s">Patch</a>' % report.id
            action += '<a href="%s" class="commit" target="__blank">Commit</a>' % url
        else:
            action += '<a href="#" class="patch" id="%s">Patch</a>' % report.id

        if report.build in [BUILD_PASS, BUILD_FAIL, BUILD_WARN]:
            build = '<a href="#" class="build" id="%s">%s</a>' % (report.id, build_name_html(report.build))
        else:
            build = build_name_html(report.build)

        fileinfo = '<a href="#" class="fileinfo" id="%s">%s</a>' % (report.id, report.file)

        reports['rows'].append({
            'id': report.id,
            'cell': {
                'id': report.id,
                'file': fileinfo,
                'title': html.escape(report.title),
                'date': report.date.strftime("%Y-%m-%d"),
                'type': report.type.name,
                'status': status_name_html(report.status),
                'build': build,
                'action': action,
                'tagname': report.tag.name,
        }}) # comment

    reports['page'] = page
    reports['total'] = reportcnt

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
def report_new(request):
    if request.method == "POST":
        tagid = get_request_paramter(request, 'tag')
        typeid = get_request_paramter(request, 'type')
        rfile = get_request_paramter(request, 'file')

        rtags = GitTag.objects.filter(id = tagid)
        if len(rtags) == 0:
            logevent("NEW: report , ERROR: tag id %s does not exists" % tagid)
            return HttpResponse('NEW: report, ERROR: tag id %s does not exists' % tagid)

        rtypes = Type.objects.filter(id = typeid)
        if len(rtypes) == 0:
            logevent("NEW: report , ERROR: type id %s does not exists" % typeid)
            return HttpResponse('NEW: report, ERROR: type id %s does not exists' % typeid)

        report = Report(tag = rtags[0], type = rtypes[0], file = rfile, status = STATUS_NEW, diff = '')
        if not os.path.exists(report.sourcefile()):
            logevent("NEW: report , ERROR: type id %s does not exists" % typeid)
            return HttpResponse('NEW: report, ERROR: type id %s does not exists' % typeid)
        report.title = rtypes[0].ptitle
        report.desc = rtypes[0].pdesc
        report.save()

        for dot in report_engine_list():
            test = dot(rtags[0].repo.dirname())
            for i in range(test.tokens()):
                if test.get_type() != rtypes[0].id:
                    test.next_token()
                    continue
                test.set_filename(rfile)
                if test.should_report():
                    text = test.get_report()
                    report.reportlog = '\n'.join(text)
                    report.save()
                break

        rtags[0].rptotal += 1
        rtags[0].save()

        logevent("NEW: report for %s, SUCCEED: new id %s" % (rfile, report.id), True)
        return HttpResponse('NEW: report for file, SUCCEED')
    else:
        repoid = int(get_request_paramter(request, 'repo', '1'))
        tagname = get_request_paramter(request, 'tag')
        context = RequestContext(request)
        context['form'] = ReportNewForm(repoid, tagname)
        return render_to_response("report/reportnew.html", context)

@login_required
@csrf_exempt
def report_edit(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if request.method == "POST":
        src = get_request_paramter(request, 'src')
        parser = PatchParser(src)
        parser.parser()

        title = parser.get_title()
        desc = parser.get_description()
        emails = parser.get_email_list()
        diff = parser.get_diff()
    
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

        register_module_name(report.file, report.module, parser.get_module_name())

        report.title = parser.get_title_full()
        report.desc = desc
        report.emails = emails
        report.module = parser.get_module_name()
        if report.diff != diff:
            report.build = 0
            report.diff = diff
            report.status = STATUS_PATCHED

        report.content = src
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
            try:
                src = srcfile.write(src)
            except:
                src = srcfile.write(unicode.encode(src, 'utf-8'))
            srcfile.close()
            diff = _get_diff_and_revert(repo.dirname(), report.file)

            user = report.username()
            email = report.email()
            title = rtype.ptitle
            desc = rtype.pdesc
            formater = PatchFormater(repo.dirname(), report.file, user, email,
                                   title, desc, diff)
            report.content = formater.format_patch()
            report.title = formater.format_title()
            report.desc = formater.format_desc()
            report.emails = formater.get_mail_list()
            report.diff = diff
            report.build = 0
            report.status = STATUS_PATCHED
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

            if report.diff != None and len(report.diff) != 0:
                try:
                    tmpsrcfname = tempfile.mktemp()
                    tmpsrcfile = open(tmpsrcfname, "w")
                    tmpsrcfile.write(src)
                    tmpsrcfile.close()

                    tmpdiffname = tempfile.mktemp()
                    tmpdiffile = open(tmpdiffname, "w")
                    tmpdiffile.write(report.diff)
                    tmpdiffile.close()

                    os.system('patch %s -i %s' % (tmpsrcfname, tmpdiffname))
                    srcfile = open(tmpsrcfname, "r")
                    src = srcfile.read()
                    srcfile.close()

                    os.unlink(tmpsrcfname)
                    os.unlink(tmpdiffname)
                except:
                    pass

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
    byver = int(get_request_paramter(request, 'version', '0'))

    repo = GitRepo.objects.filter(id = rid)
    if (len(repo) == 0):
        return render_to_response("repo id not specified")

    files = []
    idx = 1
    if byver == 1:
        reportset = Report.objects.filter(tag__name__icontains = tag_name, tag__repo = repo, mergered = 0).order_by("date")
    else:
        reportset = Report.objects.filter(tag__name = tag_name, tag__repo = repo, mergered = 0).order_by("date")
    for report in reportset:
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
    if not isinstance(shellOut, unicode):
        shellOut = unicode(shellOut, errors='ignore')

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

        apatch3 = ''
        ndir = os.path.join(os.path.dirname(rdir), 'linux-next')
        if report.tag.repo.name == 'linux.git' and os.path.exists(ndir):
            ret3, apatch3 = execute_shell('cd %s && git apply --check %s' % (ndir, temp))
            if ret3 == 0:
                apatch3 = 'patch can be apply succeed'

        ctx = '<pre># scripts/checkpatch.pl %s\n\n%s\n# git apply --check %s\n\n%s' \
                % (temp, chkpatch, temp, apatch)

        if apatch3 != '':
            ctx += '\n\n# cd ../linux-next\n# git apply --check %s\n\n%s' % (temp, apatch3)

        ctx += '</pre>'

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

        to = to.replace('"', '')
        ret, drun = execute_shell('/usr/bin/git send-email --dry-run --no-thread --to="%s" %s' \
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

        to = to.replace('"', '')
        ret, drun = execute_shell('/usr/bin/git send-email --quiet --no-thread --confirm=never --to="%s" %s' \
                                % (to, report.fullpath()))
        drun = drun.replace(report.dirname(), '')
        if ret != 0:
            ctx = '<pre>%s</pre>' % (html.escape(drun))
            ctx += '<div id="steperrors"><font color=red>Your SMTP setting is not correctly!</font></div>'
            return HttpResponse(ctx)

        report.status = STATUS_SENT
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

def report_format_gitinfo(repo, gitlog):
    lines = gitlog.split("\n")
    fileinfos = []
    for line in lines:
        if line.find('||||') == -1:
            continue
        subflds = line.split('||||')
        commit = subflds[-1]
        title = subflds[-2]
        line = '%s  %-20s' % (subflds[0], subflds[1])
        url = "%s;a=commit;h=%s" % (repo.url, commit)
        url = re.sub("git://git.kernel.org/pub/scm/", "http://git.kernel.org/?p=", url)
        fileinfos.append('%s <a href="%s" target="__blank">%s</a>' % (line, url, cgi.escape(title)))

    return '\n'.join(fileinfos)

def report_fileinfo(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    sfile = report.sourcefile()
    if not os.path.exists(sfile):
        return HttpResponse('FILEINFO, ERROR: %s does not exists' % sfile)
    rdir = report.tag.repo.dirname()
    ret, gitlog = execute_shell("cd %s; git log -n 20 --pretty=format:'%%ci||||%%an||||%%s||||%%H' %s" % (rdir, report.file))
    fileinfo = '# git log -n 20 %s\n' % report.file
    fileinfo += report_format_gitinfo(report.tag.repo, gitlog)
    ret, gitlog = execute_shell("cd %s; /usr/bin/perl ./scripts/get_maintainer.pl -f %s --remove-duplicates --scm" % (rdir, report.file))
    fileinfo += '\n\n# ./scripts/get_maintainer.pl -f %s --scm\n' % report.file    
    fileinfo += gitlog
    if report.status in [STATUS_PATCHED, STATUS_SENT]:
        count = 0
        for line in find_remove_lines(report.diff):
            ret, gitlog = execute_shell("cd %s; git log -n 1 -S '%s' --pretty=format:'%%ci||||%%an||||%%s||||%%H' %s" % (rdir, line, report.file))
            fileinfo += '\n# git log -n 1 -S \'%s\' %s\n' % (cgi.escape(line), report.file)
            fileinfo += report_format_gitinfo(report.tag.repo, gitlog)
            count += 1
            if count > 4:
                break
    return HttpResponse('<pre>%s</pre>' % fileinfo)
    
@login_required
def report_status(request):
    statusid = get_request_paramter(request, 'status')
    rids = get_request_paramter(request, 'ids')

    if rids is None:
        return HttpResponse('MARK STATUS ERROR: no patch id specified')

    if statusid is None:
        return HttpResponse('MARK STATUS ERROR: no status id specified')

    ids = rids.split(',')
    reports = []
    for i in ids:
        report = Report.objects.filter(id = i)
        if len(report) == 0:
            logevent("MARK: status [%s], ERROR: report %s does not exists" % (rids, i))
            return HttpResponse('MARK ERROR: report %s does not exists' % i)
        reports.append(report[0])

    for report in reports:
        report.status = statusid
        report.save()
        
        if report.mglist is None or len(report.mglist) == 0:
            continue

        #if rstatus.name != 'Rejected' and rstatus.name != 'Accepted':
        #    continue
        for rid in report.mglist.split(','):
            r = Report.objects.filter(id = rid)
            if len(r) == 0:
                continue

            r[0].status = statusid
            r[0].save()

    logevent("MARK: report status [%s] %s, SUCCEED" % (rids, statusid), True)
    return HttpResponse('MARK SUCCEED: report ids [%s] to %s' % (rids, statusid))

@login_required
def report_build_status(request):
    buildid = get_request_paramter(request, 'build')
    rids = get_request_paramter(request, 'ids')

    if rids is None:
        return HttpResponse('MARK BUILD ERROR: no report id specified')

    if buildid is None:
        return HttpResponse('MARK BUILD ERROR: no build id specified')

    ids = rids.split(',')
    reports = []
    for i in ids:
        report = Report.objects.filter(id = i)
        if len(report) == 0:
            logevent("MARK: build [%s], ERROR: report %s does not exists" % (rids, i))
            return HttpResponse('MARK ERROR: report %s does not exists' % i)
        reports.append(report[0])

    for report in reports:
        report.build = buildid
        report.save()
        
    logevent("MARK: report build [%s] %s, SUCCEED" % (rids, buildid), True)
    return HttpResponse('MARK SUCCEED: report ids [%s] to %s' % (rids, buildid))

@login_required
def report_merge(request):
    pids = get_request_paramter(request, 'ids')
    if pids is None:
        return HttpResponse('MERGE ERROR: no report id specified')

    ids = pids.split(',')

    if len(ids) < 2:
        return HttpResponse('MERGE ERROR: at least two report ids need')

    reports = []
    rtype = None
    tag = None
    rdir = None
    fstats = []
    fstatlen = 0
    stats = [0, 0, 0]
    diffs = ''
    logs = ''
    for i in ids:
        report = Report.objects.get(id = i)
        if not report:
            logevent("MERGE: report [%s], ERROR: report %s does not exists" % (pids, i), False)
            return HttpResponse('MERGE ERROR: report %s does not exists' % i)
            
        if report.mergered != 0:
            logevent("MERGE: report [%s], ERROR: report %s already merged" % (pids, i), False)
            return HttpResponse('MERGE ERROR: report %s already merged' % i)
            
        if rtype is None:
            rtype = report.type
        elif rtype != report.type:
            logevent("MERGE: report [%s], ERROR: report %s type different" % (pids, i))
            return HttpResponse('MERGE ERROR: report %s type different' % i)
        if tag is None:
            tag = report.tag
        elif tag != report.tag:
            logevent("MERGE: report [%s], ERROR: report %s tag different" % (pids, i))
            return HttpResponse('MERGE ERROR:, report %s tag different' % i)
        if rdir is None:
            rdir = os.path.dirname(report.file)
        elif rdir != os.path.dirname(report.file):
            logevent("MERGE: report [%s], ERROR: report %s dirname different" % (pids, i))
            return HttpResponse('MERGE ERROR: report %s dirname different' % i)

        if report.diff is None or len(report.diff) == 0:
            logevent("MERGE: report [%s], ERROR: report %s has no patch" % (pids, i))
            return HttpResponse('MERGE ERROR: report %s has no patch' % i)
            
        reports.append(report)
        logs += '\n' + report.reportlog

        lines = report.diff.split('\n')
        for i in range(len(lines)):
            if re.search(r" \S+\s+\|\s+\d+\s+[+-]+", lines[i]) != None:
                fstats.append(lines[i])
                if fstatlen < lines[i].find('|'):
                    fstatlen = lines[i].find('|')
            elif re.search(r"\d+ file[s]* changed", lines[i]) != None:
                astat = lines[i].split(',')
                for stat in astat:
                    if re.search(r"\d+ file[s]* changed", stat) != None:
                        num = stat.strip().split(' ')[0]
                        stats[0] += int(num)
                    elif stat.find('insertion') != -1:
                        num = stat.strip().split(' ')[0]
                        stats[1] += int(num)
                    elif stat.find('deletion') != -1:
                        num = stat.strip().split(' ')[0]
                        stats[2] += int(num)
            else:
                diffs += '\n'.join(lines[i:])
                break

        for i in range(len(fstats)):
            append = fstatlen - fstats[i].find('|')
            fstats[i] = fstats[i].replace('|', ' ' * append + '|')

        statline = " %d files changed" % stats[0]
        if stats[1] == 1:
            statline += ", %d insertion(+)" % stats[1]
        elif stats[1] != 0:
            statline += ", %d insertions(+)" % stats[1]
        if stats[2] == 1:
            statline += ", %d deletion(-)" % stats[2]
        elif stats[2] != 0:
            statline += ", %d deletions(-)" % stats[2]

    diffs = "%s\n%s\n%s" % ('\n'.join(fstats), statline, diffs)
    report = Report(tag = tag, file = rdir + '/', diff = diffs, reportlog = logs,
                  type = rtype, status = STATUS_PATCHED, mglist = ','.join(ids))
    report.save()

    user = report.username()
    email = report.email()

    formater = PatchFormater(tag.repo.dirname(), rdir, user, email,
                           rtype.ptitle, rtype.pdesc, diffs)
    report.content = formater.format_patch()
    report.title = formater.format_title()
    report.desc = rtype.pdesc
    report.emails = formater.get_mail_list()
    report.save()

    for p in reports:
        p.mergered = report.id
        p.save()
    tag.total -= len(reports) - 1
    tag.save()

    logevent("MERGE: report [%s], SUCCEED: new report id %s" % (pids, report.id), True)
    return HttpResponse('MERGE SUCCEED: new report id %s' % report.id)

@login_required
def report_unmerge(request):
    idsarg = get_request_paramter(request, 'ids')
    if idsarg is None:
        return HttpResponse('UNMERGE ERROR: no report id specified')

    ids = idsarg.split(',')
    reports = []
    for i in ids:
        report = Report.objects.filter(id = i)
        if len(report) == 0:
            logevent("UNMERGE: report [%s], ERROR: report %s does not exists" % (idsarg, i))
            return HttpResponse('UNMERGE ERROR: report %s does not exists' % i)

        if len(report[0].mglist) == 0:
            logevent("UNMERGE: report [%s], ERROR: report %s is not merged" % (idsarg, i))
            return HttpResponse('UNMERGE ERROR: report %s is not merged' % i)

        reports.append(report[0])

    for report in reports:
        tag = report.tag
        mglist = report.mglist.split(',')
        for pid in mglist:
            r = Report.objects.filter(id = pid)
            if len(r) == 0:
                continue
            r[0].mergered = 0
            r[0].save()
        report.delete()

        tag.total += len(mglist) - 1
        tag.save()

    logevent("UNMERGE: report [%s], SUCCEED" % (idsarg), True)
    return HttpResponse('UNMERGE SUCCEED: report ids [%s]' % idsarg)

@login_required
def report_build_all(request):
    repoid = get_request_paramter(request, 'repo', '')

    args = '%s/dailybuild.sh report %s' % (settings.BIN_DIR, repoid)
    buildlog = subprocess.Popen(args, shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    buildOut = buildlog.communicate()[0]
    if buildlog.returncode == 0:
        return HttpResponse('BUILD SUCCEED: %s' % buildOut)
    else:
        return HttpResponse('BUILD FAIL: %s' % buildOut)

@login_required
def report_special(request):
    pids = get_request_paramter(request, 'ids')
    if pids is None:
        return HttpResponse('SPECIAL ERROR: no report id specified')

    ids = pids.split(',')
    reports = []
    for i in ids:
        report = Report.objects.filter(id = i)
        if len(report) == 0:
            logevent("SPECIAL: report [%s], ERROR: patch %s does not exists" % (pids, i))
            return HttpResponse('SPECIAL ERROR: patch %s does not exists' % i)
        reports.append(report[0])

    for report in reports:
        rtype = report.type
        fname = report.file
        reason = 'special case that can not detect correctly'

        if ExceptFile.objects.filter(type = rtype, file = fname).count() == 0:
            einfo = ExceptFile(type = rtype, file = fname, reason = reason)
            einfo.save()

    logevent("SPECIAL: report [%s], SUCCEED" % pids, True)
    return HttpResponse('SPECIAL SUCCEED: patch ids [%s]' % pids)
