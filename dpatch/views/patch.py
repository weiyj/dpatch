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
import re
import tarfile
import subprocess

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils import simplejson
from django.utils import html
from django.views.decorators.csrf import csrf_exempt
from time import gmtime, strftime
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from dpatch.models import GitRepo, GitTag, Patch, Status, Event
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

def execute_shell(args):
    if isinstance(args, basestring):
        shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    else:
        shelllog = subprocess.Popen(args, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    shellOut = shelllog.communicate()[0]

    #if shelllog.returncode != 0:
    return shelllog.returncode, shellOut

def fixstrip(string, length):
    if len(string) > length:
        return string[:length - 3] + '...'
    else:
        return string

def patchlist(request, tag_name):
    context = RequestContext(request)
    context['tag'] = tag_name
    context['repo'] = get_request_paramter(request, 'repo', '1')
    return render_to_response("patch/patchlist.html", context)

def patchlistdata(request, tag_name):
    page = int(get_request_paramter(request, 'page'))
    rp = int(get_request_paramter(request, 'rp'))

    id = int(get_request_paramter(request, 'repo', '1'))

    patchs = {'page': 1, 'total': 0, 'rows': [] }
    repo = GitRepo.objects.filter(id = id)
    if (len(repo) == 0):
        return render_to_response(simplejson.dumps(patchs))

    rtag = GitTag.objects.filter(name = tag_name, repo = repo[0])
    if (len(rtag) == 0):
        return render_to_response(simplejson.dumps(patchs))

    for patch in Patch.objects.filter(tag = rtag[0], mergered = 0):
        action = ''
        action += '<a href="#" class="detail" id="%s">Detail</a>' % patch.id
        if request.user.is_authenticated() and patch.status.name == 'New':
            action += '<a href="#" class="edit" id="%s">Edit</a>' % patch.id
            action += '<a href="#" class="send" id="%s">Send</a>' % patch.id
        elif request.user.is_authenticated() and patch.status.name == 'Sent':
            action += '<a href="#" class="edit" id="%s">Edit</a>' % patch.id

        if patch.build == 0:
            build = 'TBD'
        elif patch.build == 1:
            build = '<a href="#" class="build" id="%s">PASS</a>' % patch.id
        elif patch.build == 2:
            build = '<a href="#" class="build" id="%s">FAIL</a>' % patch.id
        elif patch.build == 3:
            build = 'SKIP'

        patchs['rows'].append({
            'id': patch.id,
            'cell': {
                'id': patch.id,
                'file': fixstrip(patch.file, 40),
                'title': html.escape(fixstrip(patch.title, 60)),
                'date': patch.date.strftime("%Y-%m-%d"),
                'type': patch.type.name,
                'status': patch.status.name,
                'build': build,
                'action': action,
        }}) # comment

    if rp * page > len(patchs['rows']):
        end = len(patchs['rows'])
    else:
        end = rp * page
    start = rp * (page - 1)
    patchs['page'] = page
    patchs['total'] = len(patchs['rows'])
    patchs['rows'] = patchs['rows'][start:end]

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
        cfg.write(patch.content)
        cfg.close()

        #os.system('/usr/bin/dos2unix %s' % patch.fullpath())

        ret1, chkpatch = execute_shell('%s %s' % (cpatch, temp))
        chkpatch = chkpatch.replace(temp, 'patch')
        ret2, apatch = execute_shell('cd %s && git apply --check %s' % (rdir, temp))
        if ret2 == 0:
            apatch = 'patch can be apply succeed'

        apatch3 = ''
        if patch.tag.repo.name == 'linux.git' and os.path.exists("%s/../linux-next" % rdir):
            ret3, apatch3 = execute_shell('cd %s/../linux-next && git apply --check %s' % (rdir, temp))
            
        ctx = '<pre># scripts/checkpatch.pl %s\n\n%s\n# git apply --check %s\n\n%s' \
                % (temp, chkpatch, temp, apatch)

        if apatch3 != '':
            ctx += '\n#cd ../linux-next\n# git apply --check %s\n\n%s' % (temp, apatch3)

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

        ret, drun = execute_shell('/usr/bin/git send-email --dry-run --no-thread --to=\'%s\' %s' \
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

        ret, drun = execute_shell('/usr/bin/git send-email --quiet --no-thread --confirm=never --to=\'%s\' %s' \
                                % (to, patch.fullpath()))
        drun = drun.replace(patch.dirname(), '')
        if ret != 0:
            ctx = '<pre>%s</pre>' % (html.escape(drun))
            ctx += '<div id="steperrors"><font color=red>Your SMTP setting is not correctly!</font></div>'
            return HttpResponse(ctx)

        sent = Status.objects.filter(name = 'Sent')[0]
        patch.status = sent
        patch.save()

        ctx = '<pre>Patch has been sent succeed!</pre>'

        #if os.path.exists(patch.fullpath()):
        #    os.unlink(patch.fullpath())
    else:
        ctx = '<pre>UNKNOW step</pre>'

    return HttpResponse(ctx)

def patch_format(patch):
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
def patcheditsave(request, patch_id):
    title = get_request_paramter(request, 'title')
    desc = get_request_paramter(request, 'desc')
    emails = get_request_paramter(request, 'emails')
    diff = get_request_paramter(request, 'diff')

    if title is None or len(title) == 0:
        logevent("EDIT: patch %s, ERROR: no title specified" % patch_id)
        return HttpResponse('EDIT ERROR: no patch title specified')

    if desc is None or len(desc) == 0:
        logevent("EDIT: patch %s, ERROR: no desc specified" % patch_id)
        return HttpResponse('EDIT ERROR: no patch desc specified')

    if emails is None or len(emails) == 0:
        logevent("EDIT: patch %s, ERROR: no emails specified" % patch_id)
        return HttpResponse('EDIT ERROR: no patch emails specified')

    if diff is None or len(diff) == 0:
        logevent("EDIT: patch %s, ERROR: no diff specified" % patch_id)
        return HttpResponse('EDIT ERROR: no patch diff specified')

    patch = Patch.objects.filter(id = patch_id)
    if len(patch) == 0:
        logevent("EDIT: patch %s, ERROR: id does not exists")
        return HttpResponse('EDIT ERROR: patch id %s does not exists' % patch_id)

    patch[0].title = title
    patch[0].desc = desc
    patch[0].emails = emails
    if patch[0].diff != diff:
        patch[0].diff = diff
        patch[0].build = 0
        patch[0].status = Status.objects.get(name = 'New')
    patch[0].content = patch_format(patch[0])
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
    status = Status.objects.filter(name = 'New')[0]
    patch = Patch(tag = tag, file = rdir + '/', diff = diffs,
                  type = rtype, status = status, mglist = ','.join(ids))
    patch.save()

    user = patch.username()
    email = patch.email()

    formater = PatchFormat(tag.repo.dirname(), rdir, user, email,
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
    response['Content-Disposition'] = 'attachment; filename=patchset.tar.gz'
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
    id = int(get_request_paramter(request, 'repo', '1'))

    repo = GitRepo.objects.filter(id = id)
    if (len(repo) == 0):
        return render_to_response("repo id not specified")

    rtag = GitTag.objects.filter(name = tag_name, repo = repo[0])
    if (len(rtag) == 0):
        return render_to_response("tag id not specified")

    files = []
    idx = 1
    for patch in Patch.objects.filter(tag = rtag[0], mergered = 0).order_by("date"):
        try:
            fname = os.path.join(patch.dirname(), patch.filename(idx))
            cocci = open(fname, "w")
            cocci.write(patch.content)
            cocci.close()
            files.append(fname)
            idx = idx + 1
        except:
            pass

    response = HttpResponse(mimetype='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename=patchset.tar.gz'
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