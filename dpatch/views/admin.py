import subprocess

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from dpatch.models import GitRepo, Event

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
        action = '<a href="#" class="edit" id="%s">Edit</a>' % repo.id

        if repo.status == False:
            status = '<a href="#" class="status" id="%s">Disabled</a>' % repo.id
        else:
            status = '<a href="#" class="status" id="%s">Enabled</a>' % repo.id

        repos['rows'].append({
            'id': repo.id,
            'cell': {
                'id': repo.id,
                'name': repo.name,
                'user': repo.user,
                'email': repo.email,
                'url': repo.url,
                'status': status,
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