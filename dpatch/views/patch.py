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
import tempfile
import tarfile
import subprocess
import urllib
import urlparse
import cgi

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.utils import simplejson
from django.utils import html
from django.views.decorators.csrf import csrf_exempt
from time import gmtime, strftime
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from dpatch.models import GitRepo, GitTag, Patch, Event, Type, ExceptFile
from dpatch.lib.common.patchformater import PatchFormater
from dpatch.lib.common.patchparser import PatchParser
from dpatch.lib.db.filemodule import register_module_name
from dpatch.lib.engine.manager import patch_engine_list
from dpatch.lib.common.utils import find_remove_lines, commit_url
from dpatch.forms import PatchNewForm
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

    #if shelllog.returncode != 0:
    return shelllog.returncode, shellOut

def patchlist(request, tag_name):
    rtypes = []
    for rtype in Type.objects.filter(id__lte = 10000):
        if len(rtype.name) > 30:
            rtypes.append("%s=%s" % (rtype.name[:30], rtype.id))
        else:
            rtypes.append("%s=%s" % (rtype.name, rtype.id))

    context = RequestContext(request)
    context['tag'] = tag_name
    context['repo'] = get_request_paramter(request, 'repo', '1')
    context['types'] = '|'.join(rtypes)
    context['status'] = status_name_list([STATUS_PATCHED])
    context['build'] = build_name_list()
    return render_to_response("patch/patchlist.html", context)

def patch_list_version(request, tag_name):
    rtypes = []
    for rtype in Type.objects.filter(id__lte = 10000):
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
    context['status'] = status_name_list([STATUS_PATCHED])
    context['tagnames'] = '|'.join(rtagnames)
    context['byversion'] = True
    context['build'] = build_name_list()
    return render_to_response("patch/patchlist.html", context)

def patchfilter(pfilter):
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

def patchlistdata(request, tag_name):
    page = int(get_request_paramter(request, 'page'))
    rp = int(get_request_paramter(request, 'rp'))

    rid = int(get_request_paramter(request, 'repo', '1'))
    pfilter = get_request_paramter(request, 'filter')
    byver = int(get_request_paramter(request, 'version', '0'))

    patchs = {'page': 1, 'total': 0, 'rows': [] }

    repo = GitRepo.objects.filter(id = rid)
    if (len(repo) == 0):
        return HttpResponse(simplejson.dumps(patchs))

    rstart = rp * (page - 1)
    rend = rp * page

    if byver == 0:
        rtag = GitTag.objects.filter(name = tag_name, repo = repo[0])
        if (len(rtag) == 0):
            return HttpResponse(simplejson.dumps(patchs))

        kwargs = patchfilter(pfilter)
        patchcnt = Patch.objects.filter(tag = rtag[0], mergered = 0, **kwargs).count()
        patchset = Patch.objects.filter(tag = rtag[0], mergered = 0, **kwargs).order_by("-id")[rstart:rend]
    else:
        kwargs = patchfilter(pfilter)
        patchcnt = Patch.objects.filter(tag__name__icontains = tag_name, tag__repo = repo,
                                        mergered = 0, **kwargs).count()
        patchset = Patch.objects.filter(tag__name__icontains = tag_name, tag__repo = repo,
                                        mergered = 0, **kwargs).order_by("-id")[rstart:rend]
        
    for patch in patchset:
        action = ''
        action += '<a href="#" class="patch" id="%s">Patch</a>' % patch.id
        if request.user.is_authenticated() and patch.status == STATUS_NEW:
            if patch.mglist is None or len(patch.mglist.strip()) == 0:
                action += '<a href="#" class="fix" id="%s">Fix</a>' % patch.id
            action += '<a href="#" class="edit" id="%s">Edit</a>' % patch.id
            if patch.build in [1, 3, 4]:
                action += '<a href="#" class="send" id="%s">Send</a>' % patch.id
        elif request.user.is_authenticated() and patch.status in [STATUS_SENT, STATUS_MARKED]:
            if patch.mglist is None or len(patch.mglist.strip()) == 0:
                action += '<a href="#" class="fix" id="%s">Fix</a>' % patch.id
            action += '<a href="#" class="edit" id="%s">Edit</a>' % patch.id
        elif patch.status == STATUS_ACCEPTED and len(patch.commit) > 0:
            url = "%s;a=commit;h=%s" % (repo[0].url, patch.commit)
            url = re.sub("git://git.kernel.org/pub/scm/", "http://git.kernel.org/?p=", url)
            action += '<a href="%s" class="commit" target="__blank">Commit</a>' % url

        if patch.build in [BUILD_PASS, BUILD_FAIL, BUILD_WARN]:
            build = '<a href="#" class="build" id="%s">%s</a>' % (patch.id, build_name_html(patch.build))
        else:
            build = build_name_html(patch.build)

        fileinfo = '<a href="#" class="fileinfo" id="%s">%s</a>' % (patch.id, patch.file)

        patchs['rows'].append({
            'id': patch.id,
            'cell': {
                'id': patch.id,
                'file': fileinfo,
                'title': html.escape(patch.title),
                'date': patch.date.strftime("%Y-%m-%d"),
                'type': patch.type.name,
                'status': status_name_html(patch.status),
                'build': build,
                'action': action,
                'tagname': patch.tag.name,
        }}) # comment

    patchs['page'] = page
    patchs['total'] = patchcnt

    return HttpResponse(simplejson.dumps(patchs))

@login_required
def patchedit(request, patch_id):
    patch = Patch.objects.filter(id = patch_id)
    context = RequestContext(request)
    context['patch'] = patch[0]
    return render_to_response("patch/patchedit.html", context)

@login_required
def patchsendwizard(request, patch_id):
    context = RequestContext(request)
    context['patchid'] = patch_id
    return render_to_response("patch/patchsendwizard.html", context)

def getgitconfig(name):
    args = 'git config %s' % name
    shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
    shellOut = shelllog.communicate()[0]

    lines = shellOut.split("\n")

    return lines[0]

@csrf_exempt
def patchsendwizardstep(request, patch_id):
    patchs = Patch.objects.filter(id = patch_id)
    step = get_request_paramter(request, 'step_number', 1)

    if len(patchs) == 0:
        return HttpResponse('ERROR: patch id %s does not exists' % patch_id)

    patch = patchs[0]

    if step == '1':
        ctx = '<pre>%s</pre>' % html.escape(patch.content)
    elif step == '2':
        rdir = patch.tag.repo.dirname()
        cpatch = os.path.join(rdir, 'scripts/checkpatch.pl')

        temp = patch.fullpath()
        cfg = open(temp, "w")
        try:
            cfg.write(patch.content)
        except:
            cfg.write(unicode.encode(patch.content, 'utf-8'))
        cfg.close()

        #os.system('/usr/bin/dos2unix %s' % patch.fullpath())

        ret1, chkpatch = execute_shell('%s %s' % (cpatch, temp))
        chkpatch = chkpatch.replace(temp, 'patch')
        ret2, apatch = execute_shell('cd %s && git apply --check %s' % (rdir, temp))
        if ret2 == 0:
            apatch = 'patch can be apply succeed'

        apatch3 = ''
        ndir = os.path.join(os.path.dirname(rdir), 'linux-next')
        if patch.tag.repo.name == 'linux.git' and os.path.exists(ndir):
            ret3, apatch3 = execute_shell('cd %s && git apply --check %s' % (ndir, temp))
            if ret3 == 0:
                apatch3 = 'patch can be apply succeed'
            
        ctx = '<pre># scripts/checkpatch.pl %s\n\n%s\n# git apply --check %s\n\n%s' \
                % (temp, chkpatch, temp, apatch)

        if apatch3 != '':
            ctx += '\n\n# cd ../linux-next\n# git apply --check %s\n\n%s' % (temp, apatch3)

        ctx += '</pre>'
        ctx = ctx.replace(patch.dirname(), '')
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
            
        email = patch.emails.replace('To:', '')
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
                                % (to, patch.fullpath()))
        drun = drun.replace(patch.dirname(), '')
        if ret != 0:
            ctx = '<pre>%s</pre>' % (html.escape(drun))
            ctx += '<div id="steperrors"><font color=red>Your SMTP setting is not correctly!</font></div>'
            return HttpResponse(ctx)

        context = RequestContext(request)
        context['emails'] = emails
        context['to'] = to
        return render_to_response("patch/sendwarnning.html", context)
    elif step == '4':
        email = patch.emails
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
                                % (to, patch.fullpath()))
        drun = drun.replace(patch.dirname(), '')
        if ret != 0:
            ctx = '<pre>%s</pre>' % (html.escape(drun))
            ctx += '<div id="steperrors"><font color=red>Your SMTP setting is not correctly!</font></div>'
            return HttpResponse(ctx)

        patch.status = STATUS_SENT
        patch.save()

        ctx = '<pre>Patch has been sent succeed!</pre>'

        #if os.path.exists(patch.fullpath()):
        #    os.unlink(patch.fullpath())
    else:
        ctx = '<pre>UNKNOW step</pre>'

    return HttpResponse(ctx)

@login_required
@csrf_exempt
def patcheditsave(request, patch_id):
    src = get_request_paramter(request, 'src')
    parser = PatchParser(src)
    parser.parser()

    if len(parser.get_title()) == 0:
        logevent("EDIT: patch %s, ERROR: no title specified" % patch_id)
        return HttpResponse('EDIT ERROR: no patch title specified')

    if len(parser.get_description()) == 0:
        logevent("EDIT: patch %s, ERROR: no desc specified" % patch_id)
        return HttpResponse('EDIT ERROR: no patch desc specified')

    if len(parser.get_email_list()) == 0:
        logevent("EDIT: patch %s, ERROR: no emails specified" % patch_id)
        return HttpResponse('EDIT ERROR: no patch emails specified')

    if len(parser.get_diff()) == 0:
        logevent("EDIT: patch %s, ERROR: no diff specified" % patch_id)
        return HttpResponse('EDIT ERROR: no patch diff specified')

    patch = Patch.objects.filter(id = patch_id)
    if len(patch) == 0:
        logevent("EDIT: patch %s, ERROR: id does not exists")
        return HttpResponse('EDIT ERROR: patch id %s does not exists' % patch_id)

    register_module_name(patch[0].file, patch[0].module, parser.get_module_name())

    patch[0].title = parser.get_title_full()
    patch[0].desc = parser.get_description()
    patch[0].emails = parser.get_email_list()
    patch[0].module = parser.get_module_name()
    if patch[0].diff != parser.get_diff():
        patch[0].diff = parser.get_diff()
        patch[0].build = 0
        patch[0].status = STATUS_NEW
    patch[0].content = src
    patch[0].save()

    logevent("EDIT: patch %s, SUCCEED" % patch_id, True)
    return HttpResponse('EDIT SUCCEED')

def showpatch(request, patch_id):
    patch = Patch.objects.filter(id = patch_id)
    return render_to_response("patch/patch.html", {'patchctx': patch[0].content})

def patch_build(request, patch_id):
    patch = Patch.objects.filter(id = patch_id)
    return render_to_response("patch/patchbuild.html", {'buildlog': patch[0].buildlog})

def patch_raw(request, patch_id):
    patch = Patch.objects.filter(id = patch_id)
    if len(patch) != 0:
        return HttpResponse(patch[0].content, mimetype="text/plain")
    else:
        return HttpResponse('no such patch id')

@login_required
def patchlistmerge(request):
    pids = get_request_paramter(request, 'ids')
    if pids is None:
        return HttpResponse('MERGE ERROR: no patch id specified')

    ids = pids.split(',')

    if len(ids) < 2:
        return HttpResponse('MERGE ERROR: at least two patch ids need')

    patchs = []
    rtype = None
    tag = None
    rdir = None
    fstats = []
    fstatlen = 0
    stats = [0, 0, 0]
    diffs = ''
    for i in ids:
        patch = Patch.objects.get(id = i)
        if not patch:
            logevent("MERGE: patch [%s], ERROR: patch %s does not exists" % (pids, i), False)
            return HttpResponse('MERGE ERROR: patch %s does not exists' % i)
            
        if patch.mergered != 0:
            logevent("MERGE: patch [%s], ERROR: patch %s already merged" % (pids, i), False)
            return HttpResponse('MERGE ERROR: patch %s already merged' % i)
            
        if rtype is None:
            rtype = patch.type
        elif rtype != patch.type:
            logevent("MERGE: patch [%s], ERROR: patch %s type different" % (pids, i))
            return HttpResponse('MERGE ERROR: patch %s type different' % i)
        if tag is None:
            tag = patch.tag
        elif tag != patch.tag:
            logevent("MERGE: patch [%s], ERROR: patch %s tag different" % (pids, i))
            return HttpResponse('MERGE ERROR:, patch %s tag different' % i)
        if rdir is None:
            rdir = os.path.dirname(patch.file)
        elif rdir != os.path.dirname(patch.file):
            logevent("MERGE: patch [%s], ERROR: patch %s dirname different" % (pids, i))
            return HttpResponse('MERGE ERROR: patch %s dirname different' % i)

        patchs.append(patch)

        lines = patch.diff.split('\n')
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
    patch = Patch(tag = tag, file = rdir + '/', diff = diffs,
                  type = rtype, status = STATUS_NEW, mglist = ','.join(ids))
    patch.save()

    user = patch.username()
    email = patch.email()

    formater = PatchFormater(tag.repo.dirname(), rdir, user, email,
                           rtype.ptitle, rtype.pdesc, diffs)
    patch.content = formater.format_patch()
    patch.title = formater.format_title()
    patch.desc = rtype.pdesc
    patch.emails = formater.get_mail_list()
    patch.save()

    for p in patchs:
        p.mergered = patch.id
        p.save()
    tag.total -= len(patchs) - 1
    tag.save()

    logevent("MERGE: patch [%s], SUCCEED: new patch id %s" % (pids, patch.id), True)
    return HttpResponse('MERGE SUCCEED: new patch id %s' % patch.id)

@login_required
def patchunmerge(request):
    idsarg = get_request_paramter(request, 'ids')
    if idsarg is None:
        return HttpResponse('UNMERGE ERROR: no patch id specified')

    ids = idsarg.split(',')
    patchs = []
    for i in ids:
        patch = Patch.objects.filter(id = i)
        if len(patch) == 0:
            logevent("UNMERGE: patch [%s], ERROR: patch %s does not exists" % (idsarg, i))
            return HttpResponse('UNMERGE ERROR: patch %s does not exists' % i)

        if len(patch[0].mglist) == 0:
            logevent("UNMERGE: patch [%s], ERROR: patch %s is not merged" % (idsarg, i))
            return HttpResponse('UNMERGE ERROR: patch %s is not merged' % i)

        patchs.append(patch[0])

    for patch in patchs:
        tag = patch.tag
        mglist = patch.mglist.split(',')
        for pid in mglist:
            p = Patch.objects.filter(id = pid)
            if len(p) == 0:
                continue
            p[0].mergered = 0
            p[0].save()
        patch.delete()

        tag.total += len(mglist) - 1
        tag.save()

    logevent("UNMERGE: patch [%s], SUCCEED" % (idsarg), True)
    return HttpResponse('UNMERGE SUCCEED: patch ids [%s]' % idsarg)

@login_required
def patch_export(request):
    pids = get_request_paramter(request, 'ids')
    if pids is None:
        return HttpResponse('EXPORT ERROR: no patch id specified')

    files = []
    idx = 1
    for pid in pids.split(','):
        patch = Patch.objects.filter(id = pid)
        if len(patch) == 0:
            logevent("EXPORT: patch [%s], ERROR: id %s does not exists" % (pids, pid))
            return HttpResponse('EXPORT ERROR: id %s does not exists' % pid)
        try:
            fname = os.path.join(patch[0].dirname(), patch[0].filename(idx))
            cocci = open(fname, "w")
            cocci.write(patch[0].content)
            cocci.close()
            files.append(fname)
            idx = idx + 1
        except:
            pass

    response = HttpResponse(mimetype='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename=patchset-%s.tar.gz' % strftime("%Y%m%d%H%M%S", gmtime())
    archive = tarfile.open(fileobj=response, mode='w:gz')

    for fname in files:
        if os.path.exists(fname):
            archive.add(fname, arcname = os.path.basename(fname))

    archive.close()

    for fname in files:
        if os.path.exists(fname):
            os.unlink(fname)

    logevent("EXPORT: patch [%s], SUCCEED" % (pids), True)
    return response

@login_required
def patch_export_all(request, tag_name):
    rid = int(get_request_paramter(request, 'repo', '1'))
    byver = int(get_request_paramter(request, 'version', '0'))

    repo = GitRepo.objects.filter(id = rid)
    if (len(repo) == 0):
        return render_to_response("repo id not specified")

    files = []
    idx = 1
    if byver == 1:
        patchset = Patch.objects.filter(tag__name__icontains = tag_name, tag__repo = repo, mergered = 0).order_by("date")
    else:
        patchset = Patch.objects.filter(tag__name = tag_name, tag__repo = repo, mergered = 0).order_by("date")
    for patch in patchset:
        try:
            fname = os.path.join(patch.dirname(), patch.filename(idx))
            fpatch = open(fname, "w")
            fpatch.write(patch.content)
            fpatch.close()
            files.append(fname)
            idx = idx + 1
        except:
            pass

    response = HttpResponse(mimetype='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename=patchset-%s.tar.gz' % strftime("%Y%m%d%H%M%S", gmtime())
    archive = tarfile.open(fileobj=response, mode='w:gz')

    for fname in files:
        if os.path.exists(fname):
            archive.add(fname, arcname = os.path.basename(fname))

    archive.close()

    for fname in files:
        if os.path.exists(fname):
            os.unlink(fname)

    logevent("EXPORT: all patchs, SUCCEED", True)
    return response

@login_required
def patchdelete(request):
    pids = get_request_paramter(request, 'ids')
    if pids is None:
        return HttpResponse('DELETE ERROR: no patch id specified')

    ids = pids.split(',')
    patchs = []
    for i in ids:
        patch = Patch.objects.filter(id = i)
        if len(patch) == 0:
            logevent("DELETE: patch [%s], ERROR: patch %s does not exists" % (pids, i))
            return HttpResponse('DELETE ERROR: patch %s does not exists' % i)
        patchs.append(patch[0])

    for patch in patchs:
        tag = patch.tag
        patch.delete()

        tag.total -= 1
        tag.save()

    logevent("DELETE: patch [%s], SUCCEED" % pids, True)
    return HttpResponse('DELETE SUCCEED: patch ids [%s]' % pids)

@login_required
def patch_special(request):
    pids = get_request_paramter(request, 'ids')
    if pids is None:
        return HttpResponse('SPECIAL ERROR: no patch id specified')

    ids = pids.split(',')
    patchs = []
    for i in ids:
        patch = Patch.objects.filter(id = i)
        if len(patch) == 0:
            logevent("SPECIAL: patch [%s], ERROR: patch %s does not exists" % (pids, i))
            return HttpResponse('SPECIAL ERROR: patch %s does not exists' % i)
        patchs.append(patch[0])

    for patch in patchs:
        rtype = patch.type
        fname = patch.file
        reason = 'special case that can not detect correctly'

        if ExceptFile.objects.filter(type = rtype, file = fname).count() == 0:
            einfo = ExceptFile(type = rtype, file = fname, reason = reason)
            einfo.save()

    logevent("SPECIAL: patch [%s], SUCCEED" % pids, True)
    return HttpResponse('SPECIAL SUCCEED: patch ids [%s]' % pids)

def patchreview(request, patch_id):
    patch = Patch.objects.filter(id = patch_id)
    lines = []
    if len(patch) != 0:
        p = patch[0]
        repo = p.tag.repo
        sfile = os.path.join(repo.dirname(), p.file)
        if os.path.exists(sfile) and os.path.isfile(sfile):
            srcfile = open(sfile, "r")
            lines = srcfile.readlines()
            srcfile.close()

    context = RequestContext(request)
    context['patch'] = patch[0]
    context['src'] = ''.join(lines)

    return render_to_response("patch/review.html", context)

def _get_diff_and_revert(repo, fname):
    diff = subprocess.Popen("cd %s ; LC_ALL=en_US git diff --patch-with-stat %s" % (repo, fname),
                            shell=True, stdout=subprocess.PIPE)
    diffOut = diff.communicate()[0]
    os.system("cd %s ; git diff %s | patch -p1 -R > /dev/null" % (repo, fname))
    return diffOut

@login_required
@csrf_exempt
def patch_fix(request, patch_id):
    patch = get_object_or_404(Patch, id=patch_id)

    if request.method == "POST":
        src = get_request_paramter(request, 'src', '')

        if len(src) == 0:
            return HttpResponse('FIX: report, ERROR: no source specified')

        sfile = patch.sourcefile()
        if not os.path.exists(sfile) or not os.path.isfile(sfile):
            return HttpResponse('FIX: report, ERROR: %s does not exists' % sfile)

        try:
            rtype = patch.type
            repo = patch.tag.repo

            srcfile = open(sfile, "w")
            try:
                src = srcfile.write(src)
            except:
                src = srcfile.write(unicode.encode(src, 'utf-8'))
            srcfile.close()
            diff = _get_diff_and_revert(repo.dirname(), patch.file)

            user = patch.username()
            email = patch.email()
            if re.search(r'{{[^}]*}}', rtype.ptitle):
                title = rtype.ptitle
            else:
                title = patch.title
            if re.search(r'{{[^}]*}}', rtype.pdesc):
                desc = rtype.pdesc
            else:
                desc = patch.desc
            formater = PatchFormater(repo.dirname(), patch.file, user, email,
                                   title, desc, diff)
            patch.content = formater.format_patch()
            patch.title = formater.format_title()
            patch.desc = formater.format_desc()
            patch.emails = formater.get_mail_list()
            if patch.diff != diff:
                patch.diff = diff
                patch.status = STATUS_NEW
                patch.build = 0
            patch.save()
            return HttpResponse('FIX: patch %d, SUCCEED' % patch.id, True)
        except:
            return HttpResponse('FIX: patch, ERROR: write file error')
    else:
        context = RequestContext(request)
        sfile = patch.sourcefile()
        src = ''
        if os.path.exists(sfile) and os.path.isfile(sfile):
            srcfile = open(sfile, "r")
            src = srcfile.read()
            srcfile.close()

            try:
                tmpsrcfname = tempfile.mktemp()
                tmpsrcfile = open(tmpsrcfname, "w")
                tmpsrcfile.write(src)
                tmpsrcfile.close()
    
                tmpdiffname = tempfile.mktemp()
                tmpdiffile = open(tmpdiffname, "w")
                tmpdiffile.write(patch.diff)
                tmpdiffile.close()
    
                os.system('patch %s -i %s' % (tmpsrcfname, tmpdiffname))
                srcfile = open(tmpsrcfname, "r")
                src = srcfile.read()
                srcfile.close()

                os.unlink(tmpsrcfname)
                os.unlink(tmpdiffname)
            except:
                pass

        context['patch'] = patch
        context['src'] = src
        return render_to_response("patch/patchfix.html", context)

@login_required
@csrf_exempt
def patch_new(request):
    if request.method == "POST":
        tagid = get_request_paramter(request, 'tag')
        typeid = get_request_paramter(request, 'type')
        rfile = get_request_paramter(request, 'file')

        rtags = GitTag.objects.filter(id = tagid)
        if len(rtags) == 0:
            logevent("NEW: patch , ERROR: tag id %s does not exists" % tagid)
            return HttpResponse('NEW: patch, ERROR: tag id %s does not exists' % tagid)

        rtypes = Type.objects.filter(id = typeid)
        if len(rtypes) == 0:
            logevent("NEW: patch , ERROR: type id %s does not exists" % typeid)
            return HttpResponse('NEW: patch, ERROR: type id %s does not exists' % typeid)

        rtype = rtypes[0]
        patch = Patch(tag = rtags[0], type = rtype, file = rfile, status = STATUS_NEW, diff = '')
        if not os.path.exists(patch.sourcefile()):
            logevent("NEW: patch , ERROR: type id %s does not exists" % typeid)
            return HttpResponse('NEW: patch, ERROR: type id %s does not exists' % typeid)
        patch.save()

        for dot in patch_engine_list():
            test = dot(rtags[0].repo.dirname())
            for i in range(test.tokens()):
                if test.get_type() != rtype.id:
                    test.next_token()
                    continue
                test.set_filename(rfile)
                if test.should_patch():
                    text = test.get_patch()
                    patch.diff = text
                    user = patch.username()
                    email = patch.email()
                    formater = PatchFormater(rtags[0].repo.dirname(), rfile, user, email,
                                             rtype.ptitle, rtype.pdesc, text)
                    patch.content = formater.format_patch()
                    patch.title = formater.format_title()
                    patch.desc = formater.format_desc()
                    patch.emails = formater.get_mail_list()
                    patch.module = formater.get_module()
                    patch.save()
                break

        rtags[0].total += 1
        rtags[0].save()

        logevent("NEW: patch for %s, SUCCEED: new id %s" % (rfile, patch.id), True)
        return HttpResponse('NEW: patch for file, SUCCEED')
    else:
        repoid = int(get_request_paramter(request, 'repo', '1'))
        tagname = get_request_paramter(request, 'tag')
        context = RequestContext(request)
        context['form'] = PatchNewForm(repoid, tagname)
        return render_to_response("patch/patchnew.html", context)

@login_required
def patch_status(request):
    statusid = get_request_paramter(request, 'status')
    pids = get_request_paramter(request, 'ids')

    if pids is None:
        return HttpResponse('MARK STATUS ERROR: no patch id specified')

    if statusid is None:
        return HttpResponse('MARK STATUS ERROR: no status id specified')

    ids = pids.split(',')
    patchs = []
    for i in ids:
        patch = Patch.objects.filter(id = i)
        if len(patch) == 0:
            logevent("MARK: status [%s], ERROR: patch %s does not exists" % (pids, i))
            return HttpResponse('MARK ERROR: patch %s does not exists' % i)
        patchs.append(patch[0])

    for patch in patchs:
        patch.status = statusid
        patch.save()
        
        if patch.mglist is None or len(patch.mglist) == 0:
            continue

        #if rstatus.name != 'Rejected' and rstatus.name != 'Accepted':
        #    continue
        for pid in patch.mglist.split(','):
            p = Patch.objects.filter(id = pid)
            if len(p) == 0:
                continue

            p[0].status = statusid
            p[0].save()

    logevent("MARK: patch status [%s] %s, SUCCEED" % (pids, statusid), True)
    return HttpResponse('MARK SUCCEED: patch ids [%s] to %s' % (pids, statusid))

@login_required
def patch_build_all(request):
    repoid = get_request_paramter(request, 'repo', '')

    args = '%s/dailybuild.sh patch %s' % (settings.BIN_DIR, repoid)
    buildlog = subprocess.Popen(args, shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    buildOut = buildlog.communicate()[0]
    if buildlog.returncode == 0:
        return HttpResponse('BUILD SUCCEED: %s' % buildOut)
    else:
        return HttpResponse('BUILD FAIL: %s' % buildOut)

@login_required
def patch_build_status(request):
    buildid = get_request_paramter(request, 'build')
    pids = get_request_paramter(request, 'ids')

    if pids is None:
        return HttpResponse('MARK BUILD ERROR: no patch id specified')

    if buildid is None:
        return HttpResponse('MARK BUILD ERROR: no status id specified')

    ids = pids.split(',')
    patchs = []
    for i in ids:
        patch = Patch.objects.filter(id = i)
        if len(patch) == 0:
            logevent("MARK: build [%s], ERROR: patch %s does not exists" % (pids, i))
            return HttpResponse('MARK ERROR: patch %s does not exists' % i)
        patchs.append(patch[0])

    for patch in patchs:
        patch.build = buildid
        patch.save()

    logevent("MARK: patch build [%s] %s, SUCCEED" % (pids, buildid), True)
    return HttpResponse('MARK SUCCEED: patch ids [%s] to %s' % (pids, buildid))

def patch_format_gitinfo(repo, gitlog):
    lines = gitlog.split("\n")
    fileinfos = []
    for line in lines:
        if line.find('||||') == -1:
            continue
        subflds = line.split('||||')
        commit = subflds[-1]
        title = subflds[-2]
        line = '%s  %-20s' % (subflds[0], subflds[1])
        url = commit_url(repo.url, commit)
        fileinfos.append('%s <a href="%s" target="__blank">%s</a>' % (line, url, cgi.escape(title)))

    return '\n'.join(fileinfos)

def patch_fileinfo(request, patch_id):
    patch = Patch.objects.get(id = patch_id)
    sfile = patch.sourcefile()
    if not os.path.exists(sfile):
        return HttpResponse('FILEINFO, ERROR: %s does not exists' % sfile)
    rdir = patch.tag.repo.dirname()
    ret, gitlog = execute_shell("cd %s; git log -n 20 --pretty=format:'%%ci||||%%an||||%%s||||%%H' %s" % (rdir, patch.file))
    fileinfo = '# git log -n 20 %s\n' % patch.file
    fileinfo += patch_format_gitinfo(patch.tag.repo, gitlog)
    ret, gitlog = execute_shell("cd %s; /usr/bin/perl ./scripts/get_maintainer.pl -f %s --remove-duplicates --scm" % (rdir, patch.file))
    fileinfo += '\n\n# ./scripts/get_maintainer.pl -f %s --scm\n' % patch.file
    fileinfo += cgi.escape(gitlog)
    if patch.status in [STATUS_NEW, STATUS_SENT, STATUS_MARKED]:
        count = 0
        for line in find_remove_lines(patch.diff):
            ret, gitlog = execute_shell("cd %s; git log -n 1 -S '%s' --pretty=format:'%%ci||||%%an||||%%s||||%%H' %s" % (rdir, line, patch.file))
            fileinfo += '\n# git log -n 1 -S \'%s\' %s\n' % (cgi.escape(line), patch.file)
            fileinfo += patch_format_gitinfo(patch.tag.repo, gitlog)
            count += 1
            if count > 4:
                break

    return HttpResponse('<pre>%s</pre>' % fileinfo)

@login_required
def patch_stable(request):
    pids = get_request_paramter(request, 'ids')
    if pids is None:
        return HttpResponse('STABLE ERROR: no patch id specified')

    ids = pids.split(',')
    patchs = []
    for i in ids:
        patch = Patch.objects.filter(id = i)
        if len(patch) == 0:
            logevent("STABLE: patch [%s], ERROR: patch %s does not exists" % (pids, i))
            return HttpResponse('STABLE ERROR: patch %s does not exists' % i)
        patchs.append(patch[0])

    for patch in patchs:
        ntag = GitTag.objects.filter(repo__id = 1).order_by("-id")
        if len(ntag) == 0:
            continue
        patch.tag.total = patch.tag.total - 1
        patch.tag.save()
        patch.tag = ntag[0]
        patch.save()
        patch.tag.total = patch.tag.total + 1
        patch.tag.save()

    logevent("STABLE: patch [%s], SUCCEED" % pids, True)
    return HttpResponse('STABLE SUCCEED: patch ids [%s]' % pids)
