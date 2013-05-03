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
import subprocess
import tempfile

from time import gmtime, strftime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from dpatch.models import GitRepo, Event, SysConfig

def logevent(event, status = False):
    evt = Event(event = event, status = status)
    evt.save()

def gitrepo(request):
    context = RequestContext(request)
    return render_to_response("admin/gitrepo.html", context)

def gitrepolist(request):
    page = int(request.GET.get('page', '1'))
    rp = int(request.GET.get('rp', '15'))

    repos = {'page': 1, 'total': 0, 'rows': [] }
    for repo in GitRepo.objects.all():
        action = '<a href="#" class="edit" id="%s">EDIT</a>' % repo.id

        if repo.status == False:
            status = '<a href="#" class="status" id="%s">DISABLED</a>' % repo.id
        else:
            status = '<a href="#" class="status" id="%s">ENABLED</a>' % repo.id

        if repo.build == False:
            build = '<a href="#" class="build" id="%s">DISABLED</a>' % repo.id
        else:
            build = '<a href="#" class="build" id="%s">ENABLED</a>' % repo.id

        repos['rows'].append({
            'id': repo.id,
            'cell': {
                'id': repo.id,
                'name': repo.name,
                'user': repo.user,
                'email': repo.email,
                'url': repo.url,
                'status': status,
                'build': build,
                'update': repo.update.strftime("%Y-%m-%d %H:%M:%S"),
                'action': action,
        }}) # comment

    if rp * page > len(repos['rows']):
        end = len(repos['rows'])
    else:
        end = rp * page
    start = rp * (page - 1)
    repos['page'] = page
    repos['total'] = len(repos['rows'])
    repos['rows'] = repos['rows'][start:end]

    return HttpResponse(simplejson.dumps(repos))

@login_required
def git_repo_enable(request, repo_id):
    repo = GitRepo.objects.filter(id = repo_id)
    if len(repo) == 0:
        logevent('ENABLE: git repo, ERROR: id %s does not exists' % repo_id)
        return HttpResponse('ENABLE ERROR: id %s does not exists' % repo_id)

    repo[0].status = not repo[0].status
    repo[0].save()

    logevent('ENABLE: git repo, SUCCEED: status change to %s' % repo[0].status, True)
    return HttpResponse('ENABLE SUCCEED: type id %s' % repo_id)

@login_required
def git_repo_enable_build(request, repo_id):
    repo = GitRepo.objects.filter(id = repo_id)
    if len(repo) == 0:
        logevent('ENABLE: git repo build, ERROR: id %s does not exists' % repo_id)
        return HttpResponse('ENABLE ERROR: id %s does not exists' % repo_id)

    repo[0].build = not repo[0].build
    repo[0].save()

    logevent('ENABLE: git repo build, SUCCEED: status change to %s' % repo[0].build, True)
    return HttpResponse('ENABLE SUCCEED: type id %s' % repo_id)

@login_required
@csrf_exempt
def gitrepoadd(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        user = request.POST.get('user', '')
        mail = request.POST.get('email', '')
        url = request.POST.get('url', '')

        if name == '':
            logevent("NEW GIT ERROR: no name specified")
            return HttpResponse('NEW GIT ERROR: no name specified')

        if user == '':
            logevent("NEW GIT ERROR: no user specified")
            return HttpResponse('NEW GIT ERROR: no user specified')

        if mail == '':
            logevent("NEW GIT ERROR: no email specified")
            return HttpResponse('NEW GIT ERROR: no email specified')

        if url == '':
            logevent("NEW GIT ERROR: no url specified")
            return HttpResponse('NEW GIT ERROR: no url specified')

        repo = GitRepo(name = name, user = user, email = mail, url = url)
        repo.save()
        logevent("NEW GIT SUCCEED: new id %s" % repo.id, True)
        return HttpResponse('NEW GIT SUCCEED: new id %s' % repo.id)
    else:
        context = RequestContext(request)
        return render_to_response("admin/gitrepoadd.html", context)

@login_required
@csrf_exempt
def gitrepodelete(request):
    pids = request.GET.get('ids', None)
    if pids is None:
        return HttpResponse('DELETE ERROR: no git repo id specified')

    ids = pids.split(',')
    repos = []
    for i in ids:
        repo = GitRepo.objects.filter(id = i)
        if len(repo) == 0:
            logevent("DELETE: repo [%s], ERROR: repo %s does not exists" % (pids, i))
            return HttpResponse('DELETE ERROR: repo %s does not exists' % i)
        repos.append(repo[0])

    for repo in repos:
        repo.delete()

    logevent("DELETE: repo [%s], SUCCEED" % pids, True)
    return HttpResponse('DELETE SUCCEED: repo ids [%s]' % pids)

@login_required
@csrf_exempt
def git_repo_edit(request, repo_id):
    if request.method == "POST":
        name = request.POST.get('name', '')
        user = request.POST.get('user', '')
        mail = request.POST.get('email', '')
        url = request.POST.get('url', '')

        if name == '':
            logevent("EDIT: git repo, ERROR: no name specified")
            return HttpResponse('EDIT ERROR: no name specified')

        if user == '':
            logevent("EDIT: git repo, ERROR: no user specified")
            return HttpResponse('EDIT ERROR: no user specified')

        if mail == '':
            logevent("EDIT: git repo, ERROR: no email specified")
            return HttpResponse('NEW ERROR: no email specified')

        if url == '':
            logevent("EDIT: git repo, ERROR: no url specified")
            return HttpResponse('NEW ERROR: no url specified')

        repos = GitRepo.objects.filter(id = repo_id)
        if len(repos) == 0:
            logevent("EDIT: git repo, ERROR: id %s does not exists" % repo_id)
            return HttpResponse('EDIT ERROR: repo id %s does not exists' % repo_id)

        repo = repos[0]
        repo.name = name
        repo.user = user
        repo.email = mail
        repo.url = url
        repo.save()

        logevent("EDIT: git repo, SUCCEED: id %s" % repo_id, True)
        return HttpResponse('EDIT: git repo, SUCCEED: id %s' % repo_id)
    else:
        repos = GitRepo.objects.filter(id = repo_id)
        if len(repos) == 0:
            repo = None
        else:
            repo = repos[0]
        context = RequestContext(request)
        context['repo'] = repo
        return render_to_response("admin/gitrepoadd.html", context)

def execute_shell(args):
    if isinstance(args, basestring):
        shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
    else:
        shelllog = subprocess.Popen(args, stdout=subprocess.PIPE)
    shellOut = shelllog.communicate()[0]

    lines = shellOut.split("\n")

    return lines[0]

@login_required
@csrf_exempt
def git_email(request):
    if request.method == "POST":
        server = request.POST.get('server', '')
        port = request.POST.get('port', '')
        crypt = request.POST.get('crypt', '')
        user = request.POST.get('user', '')
        password = request.POST.get('password', '')
        mfrom = request.POST.get('from', '')

        if server == '':
            logevent("EDIT: SMTP server, ERROR: no server specified")
            return HttpResponse('EDIT SMTP: no server specified')

        if port == '':
            logevent("EDIT: SMTP server, ERROR: no port specified")
            return HttpResponse('EDIT SMTP: no port specified')

        if crypt == '':
            logevent("EDIT: SMTP server, ERROR: no encryption specified")
            return HttpResponse('EDIT SMTP: no encryption specified')

        if user == '':
            logevent("EDIT: SMTP server, ERROR: no user specified")
            return HttpResponse('EDIT SMTP: no username specified')

        if password == '':
            logevent("EDIT: SMTP server, ERROR: no password specified")
            return HttpResponse('EDIT SMTP: no password specified')

        if mfrom == '':
            logevent("EDIT: SMTP server, ERROR: no email specified")
            return HttpResponse('EDIT SMTP: no email specified')

        execute_shell('git config --global sendemail.smtpencryption %s' % crypt)
        execute_shell('git config --global sendemail.smtpserver %s' % server)
        execute_shell('git config --global sendemail.smtpserverport %s' % port)
        execute_shell('git config --global sendemail.smtpuser %s' % user)
        execute_shell('git config --global sendemail.smtppass %s' % password)
        execute_shell('git config --global sendemail.from \'%s\'' % mfrom)

        #'git config --global sendemail.from'
        logevent("EDIT: SMTP server, SUCCEED", True)
        return HttpResponse('EDIT SMTP SUCCEED')
    else:
        context = RequestContext(request)
        
        smtpencryption = execute_shell('git config sendemail.smtpencryption')
        smtpserver = execute_shell('git config sendemail.smtpserver')
        smtpserverport = execute_shell('git config sendemail.smtpserverport')
        smtpuser = execute_shell('git config sendemail.smtpuser')
        smtppass = execute_shell('git config sendemail.smtppass')
        mfrom = execute_shell('git config sendemail.from')
    
        context['smtpencryption'] = smtpencryption
        context['smtpserver'] = smtpserver
        context['smtpserverport'] = smtpserverport
        context['smtpuser'] = smtpuser
        context['smtppass'] = smtppass
        context['from'] = mfrom
    
        return render_to_response("admin/gitemail.html", context)
    
@login_required
@csrf_exempt
def git_email_test(request):
    if request.method == "POST":
        cfrom = execute_shell('git config sendemail.from')
        mfrom = request.POST.get('from', cfrom)
        mto = request.POST.get('to', cfrom)
        subject = request.POST.get('subject', 'test mail')
        mbody = request.POST.get('mbody', 'This is a test mail')

        mail = "Content-Type: text/plain; charset=ISO-8859-1\n"
        mail += "Content-Transfer-Encoding: 7bit\n"
        mail += "From: %s\n" % (mfrom)
        mail += "Date: %s\n" % strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        mail += "Subject: %s\n" % subject
        mail += "To: %s\n" % mto
        mail += "\n%s\n\n" % mbody

        tmpfname = tempfile.mktemp()
        mfile = open(tmpfname, "w")
        mfile.write(mail)
        mfile.close()

        drun = execute_shell('/usr/bin/git send-email --quiet --no-thread --confirm=never --to="%s" %s' \
                                % (mto, tmpfname))
        os.unlink(tmpfname)
        return HttpResponse('TEST MAIL SEND: %s' % drun)
    else:
        context = RequestContext(request)
        context['from'] = execute_shell('git config sendemail.from')
        return render_to_response("admin/gitemailtest.html", context)

def sys_config(request):
    context = RequestContext(request)
    return render_to_response("admin/sysconfig.html", context)

def sys_config_list(request):
    page = int(request.GET.get('page', '1'))
    rp = int(request.GET.get('rp', '15'))

    settings = {'page': 1, 'total': 0, 'rows': [] }
    for config in SysConfig.objects.all():
        settings['rows'].append({
            'id': config.id,
            'cell': {
                'id': config.id,
                'name': config.name,
                'value': config.value,
        }}) # comment

    if rp * page > len(settings['rows']):
        end = len(settings['rows'])
    else:
        end = rp * page
    start = rp * (page - 1)
    settings['page'] = page
    settings['total'] = len(settings['rows'])
    settings['rows'] = settings['rows'][start:end]

    return HttpResponse(simplejson.dumps(settings))
