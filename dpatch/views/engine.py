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
import tempfile
import subprocess

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from time import gmtime, strftime

from dpatch.models import CocciEngine, CocciReport, Type, Event, Patch, Report, ExceptFile
from dpatch.forms import ExceptFileForm

def get_request_paramter(request, key):
    if request.GET.has_key(key):
        return request.GET[key]
    elif request.POST.has_key(key):
        return request.POST[key]
    return None

def logevent(event, status = False):
    evt = Event(event = event, status = status)
    evt.save()

def semantic(request):
    context = RequestContext(request)
    return render_to_response("engine/coccisemantic.html", context)

def enabletype(request, type_id):
    rtype = Type.objects.filter(id = type_id)
    if len(rtype) == 0:
        return HttpResponse('ENABLED: ERROR: type id %s does not exists' % type_id)

    rtype[0].status = not rtype[0].status
    rtype[0].save()
    return HttpResponse('ENABLED: SUCCEED: type id %s' % type_id)

@login_required
@csrf_exempt
def semantic_edit(request, cocci_id):
    if request.method == "POST":
        name = get_request_paramter(request, 'name')
        title = get_request_paramter(request, 'title')
        desc = get_request_paramter(request, 'desc')
        content = get_request_paramter(request, 'content')
        options = get_request_paramter(request, 'options')
        fixed = get_request_paramter(request, 'fixed')

        if name is None or len(name) == 0:
            logevent("EDIT: coccinelle semantic, ERROR: no name specified")
            return HttpResponse('EDIT ERROR: no semantic name specified')
    
        if title is None or len(title) == 0:
            logevent("EDIT: coccinelle semantic, ERROR: no title specified")
            return HttpResponse('EDIT ERROR: no semantic title specified')
    
        if desc is None or len(desc) == 0:
            logevent("EDIT: coccinelle semantic, ERROR: no desc specified")
            return HttpResponse('EDIT ERROR: no semantic desc specified')
    
        if content is None or len(content) == 0:
            logevent("EDIT: coccinelle semantic, ERROR: no content specified")
            return HttpResponse('EDIT ERROR: no semantic content specified')

        if options is None:
            options = ''

        if fixed is None:
            fixed = ''

        coccis = CocciEngine.objects.filter(id = cocci_id)
        if len(coccis) == 0:
            logevent("EDIT: coccinelle semantic, ERROR: id %s does not exists" % cocci_id)
            return HttpResponse('EDIT ERROR: semantic id %s does not exists' % cocci_id)

        engine = coccis[0]
        ofname = engine.fullpath()
        fname = '%s.cocci' % name.strip()
        engine.file = fname
        engine.content = content
        engine.options = options.strip()
        engine.fixed = fixed.strip()

        rtype = Type.objects.get(id = engine.id + 3000)

        einfo = []
        for efile in ExceptFile.objects.filter(type = rtype):
            einfo.append({'file': efile.file, 'reason': efile.reason})

        spctx = engine.rawformat(title, desc, einfo)
        try:
            cocci = open(engine.fullpath(), "w")
            cocci.write(spctx)
            cocci.close()
            if ofname != engine.fullpath() and os.path.exists(ofname):
                os.unlink(ofname)
        except:
            logevent("EDIT: coccinelle semantic, ERROR: can not write file %s" % engine.fullpath())
            return HttpResponse('EDIT ERROR: can not write file %s' % engine.fullpath())

        engine.save()
    
        rtype.name = name
        rtype.ptitle = title
        rtype.pdesc = desc
        rtype.save()

        logevent("EDIT: coccinelle semantic, SUCCEED: type id %s" % rtype.id, True)
        return HttpResponse('EDIT: coccinelle semantic, SUCCEED: type id %s' % cocci_id)
    else:
        coccis = CocciEngine.objects.filter(id = cocci_id)
        if len(coccis) == 0:
            engine = None
            rtype = None
        else:
            engine = coccis[0]
            rtype = Type.objects.get(id = engine.id + 3000)
        context = RequestContext(request)
        context['cocci'] = engine
        context['type'] = rtype
        return render_to_response("engine/semanticedit.html", context)

def semantic_detail(request, cocci_id):
    coccis = CocciEngine.objects.filter(id = cocci_id)
    if len(coccis) == 0:
        return ""
    cocci = coccis[0]
    try:
        cfile = open(cocci.fullpath(), 'r')
        content = cfile.read()
        cfile.close()
    except:
        content = cocci.content
    context = RequestContext(request)
    context['content'] = content
    return render_to_response("engine/coccidetail.html", context)

@login_required
@csrf_exempt
def semantic_delete(request):
    pids = get_request_paramter(request, 'ids')
    if pids is None:
        return HttpResponse('DELETE ERROR: no patch id specified')

    ids = pids.split(',')
    coccis = []
    for i in ids:
        cocci = CocciEngine.objects.filter(id = i)
        if len(cocci) == 0:
            logevent("DELETE: coccinelle semantic [%s], ERROR: id %s does not exists" % (pids, i))
            return HttpResponse('DELETE ERROR: id %s does not exists' % i)
        coccis.append(cocci[0])

    for cocci in coccis:
        rtypes = Type.objects.filter(id = cocci.id + 3000)
        if len(rtypes) != 0:
            rtype = rtypes[0]

            # delete patchs owner by this type
            patchs = Patch.objects.filter(type = rtype)
            for patch in patchs:
                tag = patch.tag
                patch.delete()
                tag.total -= 1
                tag.save()

            # delete except files owner by this type
            efiles = ExceptFile.objects.filter(type = rtype)
            for efile in efiles:
                efile.delete()

            rtype.delete()
        if os.path.exists(cocci.fullpath()):
            os.unlink(cocci.fullpath())
        cocci.delete()

    logevent("DELETE: coccinelle semantic [%s], SUCCEED" % pids, True)
    return HttpResponse('DELETE SUCCEED: engine ids [%s]' % pids)

@login_required
@csrf_exempt
def semantic_new(request):
    if request.method == "POST":
        name = get_request_paramter(request, 'name')
        title = get_request_paramter(request, 'title')
        desc = get_request_paramter(request, 'desc')
        content = get_request_paramter(request, 'content')
        options = get_request_paramter(request, 'options')
        fixed = get_request_paramter(request, 'fixed')

        if name is None or len(name) == 0:
            logevent("NEW: coccinelle semantic, ERROR: no name specified")
            return HttpResponse('NEW ERROR: no semantic name specified')
    
        if title is None or len(title) == 0:
            logevent("NEW: coccinelle semantic, ERROR: no title specified")
            return HttpResponse('NEW ERROR: no semantic title specified')
    
        if desc is None or len(desc) == 0:
            logevent("NEW: coccinelle semantic, ERROR: no desc specified")
            return HttpResponse('NEW ERROR: no semantic desc specified')
    
        if content is None or len(content) == 0:
            logevent("NEW: coccinelle semantic, ERROR: no content specified")
            return HttpResponse('NEW ERROR: no semantic content specified')
    
        if options is None:
            options = ''

        if fixed is None:
            fixed = ''

        fname = '%s.cocci' % name.strip()
        engine = CocciEngine(file = fname, content = content, options = options, fixed = fixed.strip())
        if os.path.exists(engine.fullpath()):
            logevent("NEW: coccinelle semantic, ERROR: name %s already exists" % name)
            return HttpResponse('NEW ERROR: semantic name %s already exists' % name)

        spctx = engine.rawformat(title, desc)
        try:
            cocci = open(engine.fullpath(), "w")
            cocci.write(spctx)
            cocci.close()
        except:
            logevent("NEW: coccinelle semantic, ERROR: can not write file %s" % engine.fullpath())
            return HttpResponse('NEW ERROR: can not write file %s' % engine.fullpath())
    
        engine.save()
    
        rtype = Type(id = engine.id + 3000, name = name, ptitle = title, pdesc = desc, status = False)
        rtype.save()
    
        logevent("NEW: coccinelle semantic, SUCCEED: new type id %s" % rtype.id, True)
        return HttpResponse('NEW: coccinelle semanticm, SUCCEED: new type %s' % rtype.id)
    else:
        context = RequestContext(request)
        return render_to_response("engine/semanticedit.html", context)

def semantic_list(request):
    page = int(get_request_paramter(request, 'page'))
    rp = int(get_request_paramter(request, 'rp'))

    coccis = {'page': 1, 'total': 0, 'rows': [] }
    for cocci in CocciEngine.objects.all():
        rtype = Type.objects.get(id = cocci.id + 3000)
        if rtype.status == False:
            status = '<a href="#" class="status" id="%s">Disabled</a>' % rtype.id
        else:
            status = '<a href="#" class="status" id="%s">Enabled</a>' % rtype.id

        action = '<a href="#" class="detail" id="%s">Detail</a>' % cocci.id
        if request.user.is_authenticated():
            action += '<a href="#" class="edit" id="%s">Edit</a>' % cocci.id

        coccis['rows'].append({
            'id': cocci.id,
            'cell': {
                'id': cocci.id,
                'file': cocci.file,
                'status': status,
                'name': rtype.name,
                'title': rtype.ptitle,
                'desc': rtype.pdesc,
                'options': '-',
                'action': action,
        }}) # comment

    if rp * page > len(coccis['rows']):
        end = len(coccis['rows'])
    else:
        end = rp * page
    start = rp * (page - 1)
    coccis['page'] = page
    coccis['total'] = len(coccis['rows'])
    coccis['rows'] = coccis['rows'][start:end]

    return HttpResponse(simplejson.dumps(coccis))

def rewrite_engine(cocci):
    rtypes = Type.objects.filter(id = cocci.id + 3000)
    if len(rtypes) != 0:
        rtype = rtypes[0]

        einfo = []
        for efile in ExceptFile.objects.filter(type = rtype):
            einfo.append({'file': efile.file, 'reason': efile.reason})

        if len(einfo) > 0:
            spctx = cocci.rawformat(rtype.ptitle, rtype.pdesc, einfo)
            try:
                cocci = open(cocci.fullpath(), "w")
                cocci.write(spctx)
                cocci.close()
            except:
                pass

@login_required
@csrf_exempt
def semantic_import(request):
    fp = request.FILES['file']
    if fp != None:
        if os.path.splitext(fp.name)[1] == ".cocci":
            fname = os.path.join('/tmp', fp.name)
        else:
            fname = tempfile.mktemp()

        with open(fname, 'w+') as destination:
            for chunk in fp.chunks():
                destination.write(chunk)

        args = '/usr/dpatch/bin/importcocci.sh %s' % fname
        shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
        shellOut = shelllog.communicate()[0]

        if os.path.exists(fname):
            os.unlink(fname)

        logevent("IMPORT: coccinelle semantic, SUCCEED", True)
        return HttpResponse(shellOut)
    else:
        return HttpResponse('IMPORT ERROR: no file found')

def semantic_export(request):
    cids = get_request_paramter(request, 'ids')
    if cids is None:
        return HttpResponse('EXPORT ERROR: no patch id specified')

    files = []
    for cid in cids.split(','):
        cocci = CocciEngine.objects.filter(id = cid)
        if len(cocci) == 0:
            logevent("EXPORT: coccinelle semantic [%s], ERROR: id %s does not exists" % (cids, cid))
            return HttpResponse('EXPORT ERROR: id %s does not exists' % cid)
        rewrite_engine(cocci[0])
        files.append(cocci[0].fullpath())

    response = HttpResponse(mimetype='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename=cocci-semantics-%s.tar.gz' % strftime("%Y%m%d%H%M%S", gmtime())
    archive = tarfile.open(fileobj=response, mode='w:gz')

    for fname in files:
        if os.path.exists(fname):
            archive.add(fname, arcname = os.path.basename(fname))

    archive.close()

    logevent("EXPORT: coccinelle semantic [%s], SUCCEED" % (cids), True)
    return response

def semantic_export_all(request):
    files = []
    for cocci in CocciEngine.objects.all():
        rewrite_engine(cocci)
        files.append(cocci.fullpath())

    response = HttpResponse(mimetype='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename=cocci-semantics-all-%s.tar.gz' % strftime("%Y%m%d%H%M%S", gmtime())
    archive = tarfile.open(fileobj=response, mode='w:gz')

    for fname in files:
        if os.path.exists(fname):
            archive.add(fname, arcname = os.path.basename(fname))

    archive.close()

    logevent("EXPORT: coccinelle semantic all, SUCCEED", True)
    return response

@login_required
@csrf_exempt
def semantic_move_to_report(request):
    sids = get_request_paramter(request, 'ids')
    if sids is None:
        return HttpResponse('MOVE ERROR: no semantic id specified')

    ids = sids.split(',')
    coccis = []
    for i in ids:
        cocci = CocciEngine.objects.filter(id = i)
        if len(cocci) == 0:
            logevent("MOVE: coccinelle semantic [%s], ERROR: id %s does not exists" % (sids, i))
            return HttpResponse('MOVE ERROR: id %s does not exists' % i)
        coccis.append(cocci[0])

    for cocci in coccis:
        rtypes = Type.objects.filter(id = cocci.id + 3000)
        if len(rtypes) != 0:
            rtype = rtypes[0]

            patchs = Patch.objects.filter(type = rtype)
            efiles = ExceptFile.objects.filter(type = rtype)

            ncocci = CocciReport(file = cocci.file, options = cocci.options, content = cocci.content)
            ncocci.save()
            rewrite_report_engine(ncocci)

            rtype.id = ncocci.id + 10000
            rtype.save()
                
            # move patchs owner by this type
            for patch in patchs:
                report = Report(tag = patch.tag, type = rtype, status = patch.status,
                                file = patch.file, date = patch.date, mergered = 0,
                                mglist = '', commit = patch.commit, reportlog = patch.diff,
                                diff = patch.diff, title = patch.title, desc = patch.desc,
                                emails = patch.emails, content = patch.content,
                                build = patch.build, buildlog = patch.buildlog)
                report.save()
                tag = patch.tag
                patch.delete()
                tag.total -= 1
                tag.rptotal += 1
                tag.save()

            # delete except files owner by this type
            for efile in efiles:
                efile.type = rtype
                efile.save()

        if os.path.exists(cocci.fullpath()):
            os.unlink(cocci.fullpath())
        cocci.delete()

    logevent("MOVE: coccinelle semantic [%s], SUCCEED" % sids, True)
    return HttpResponse('MOVE SUCCEED: engine ids [%s]' % sids)


def exceptfile(request):
    context = RequestContext(request)
    return render_to_response("engine/exceptfiles.html", context)

def exceptfile_list(request):
    page = int(get_request_paramter(request, 'page'))
    rp = int(get_request_paramter(request, 'rp'))

    efiles = {'page': 1, 'total': 0, 'rows': [] }
    for efile in ExceptFile.objects.all():
        efiles['rows'].append({
            'id': efile.id,
            'cell': {
                'id': efile.id,
                'type': efile.type.name,
                'file': efile.file,
                'reason': efile.reason,
        }}) # comment

    if rp * page > len(efiles['rows']):
        end = len(efiles['rows'])
    else:
        end = rp * page
    start = rp * (page - 1)
    efiles['page'] = page
    efiles['total'] = len(efiles['rows'])
    efiles['rows'] = efiles['rows'][start:end]

    return HttpResponse(simplejson.dumps(efiles))

@login_required
@csrf_exempt
def exceptfile_new(request):
    if request.method == "POST":
        typeid = get_request_paramter(request, 'type')
        fname = get_request_paramter(request, 'file')
        reason = get_request_paramter(request, 'reason')

        rtypes = Type.objects.filter(id = typeid)
        if len(rtypes) == 0:
            logevent("NEW: except file, ERROR: type id %s does not exists" % typeid)
            return HttpResponse('NEW: except file, ERROR: type id %s does not exists' % typeid)

        einfo = ExceptFile(type = rtypes[0], file = fname, reason = reason)
        einfo.save()

        if int(typeid) > 3000:
            coccis = CocciEngine.objects.filter(id = int(typeid) - 3000)
            if len(coccis) > 0:
                rewrite_engine(coccis[0])

        logevent("NEW: except file, SUCCEED: new id %s" % einfo.id, True)
        return HttpResponse('NEW: except file, SUCCEED')
    else:
        context = RequestContext(request)
        context['form'] = ExceptFileForm()
        return render_to_response("engine/exceptfilesedit.html", context)

@login_required
@csrf_exempt
def exceptfile_delete(request):
    tids = get_request_paramter(request, 'ids')
    if tids is None:
        return HttpResponse('DELETE ERROR: no id specified')

    ids = tids.split(',')
    einfos = []
    for i in ids:
        einfo = ExceptFile.objects.filter(id = i)
        if len(einfo) == 0:
            logevent("DELETE: except file [%s], ERROR: id %s does not exists" % (tids, i))
            return HttpResponse('DELETE ERROR: except file %s does not exists' % i)
        einfos.append(einfo[0])

    for einfo in einfos:
        typeid = einfo.type.id
        einfo.delete()
        if typeid > 3000:
            coccis = CocciEngine.objects.filter(id = typeid - 3000)
            if len(coccis) > 0:
                rewrite_engine(coccis[0])

    logevent("DELETE: except file [%s], SUCCEED" % tids, True)
    return HttpResponse('DELETE SUCCEED: except file ids [%s]' % tids)

def report_semantic(request):
    context = RequestContext(request)
    return render_to_response("engine/reportengine.html", context)

def report_semantic_list(request):
    page = int(get_request_paramter(request, 'page'))
    rp = int(get_request_paramter(request, 'rp'))

    coccis = {'page': 1, 'total': 0, 'rows': [] }
    for cocci in CocciReport.objects.all():
        rtype = Type.objects.get(id = cocci.id + 10000)
        if rtype.status == False:
            status = '<a href="#" class="status" id="%s">Disabled</a>' % rtype.id
        else:
            status = '<a href="#" class="status" id="%s">Enabled</a>' % rtype.id

        action = '<a href="#" class="detail" id="%s">Detail</a>' % cocci.id
        if request.user.is_authenticated():
            action += '<a href="#" class="edit" id="%s">Edit</a>' % cocci.id

        coccis['rows'].append({
            'id': cocci.id,
            'cell': {
                'id': cocci.id,
                'file': cocci.file,
                'status': status,
                'name': rtype.name,
                'title': rtype.ptitle,
                'desc': rtype.pdesc,
                'options': '-',
                'action': action,
        }}) # comment

    if rp * page > len(coccis['rows']):
        end = len(coccis['rows'])
    else:
        end = rp * page
    start = rp * (page - 1)
    coccis['page'] = page
    coccis['total'] = len(coccis['rows'])
    coccis['rows'] = coccis['rows'][start:end]

    return HttpResponse(simplejson.dumps(coccis))

@login_required
@csrf_exempt
def report_semantic_new(request):
    if request.method == "POST":
        name = get_request_paramter(request, 'name')
        title = get_request_paramter(request, 'title')
        desc = get_request_paramter(request, 'desc')
        content = get_request_paramter(request, 'content')
        options = get_request_paramter(request, 'options')

        if name is None or len(name) == 0:
            logevent("NEW: coccinelle report semantic, ERROR: no name specified")
            return HttpResponse('NEW ERROR: no semantic name specified')
    
        if title is None or len(title) == 0:
            logevent("NEW: coccinelle report semantic, ERROR: no title specified")
            return HttpResponse('NEW ERROR: no semantic title specified')
    
        if desc is None or len(desc) == 0:
            logevent("NEW: coccinelle report semantic, ERROR: no desc specified")
            return HttpResponse('NEW ERROR: no semantic desc specified')
    
        if content is None or len(content) == 0:
            logevent("NEW: coccinelle report semantic, ERROR: no content specified")
            return HttpResponse('NEW ERROR: no semantic content specified')
    
        if options is None:
            options = ''

        fname = '%s.cocci' % name.strip()
        engine = CocciReport(file = fname, content = content, options = options)
        if os.path.exists(engine.fullpath()):
            logevent("NEW: coccinelle report semantic, ERROR: name %s already exists" % name)
            return HttpResponse('NEW ERROR: semantic name %s already exists' % name)

        spctx = engine.rawformat(title, desc)
        try:
            cocci = open(engine.fullpath(), "w")
            cocci.write(spctx)
            cocci.close()
        except:
            logevent("NEW: coccinelle report semantic, ERROR: can not write file %s" % engine.fullpath())
            return HttpResponse('NEW ERROR: can not write file %s' % engine.fullpath())
    
        engine.save()
    
        rtype = Type(id = engine.id + 10000, name = name, ptitle = title, pdesc = desc, status = False)
        rtype.save()
    
        logevent("NEW: coccinelle report semantic, SUCCEED: new type id %s" % rtype.id, True)
        return HttpResponse('NEW: coccinelle report semanticm, SUCCEED: new type %s' % rtype.id)
    else:
        context = RequestContext(request)
        return render_to_response("engine/reportedit.html", context)

@login_required
@csrf_exempt
def report_semantic_delete(request):
    pids = get_request_paramter(request, 'ids')
    if pids is None:
        return HttpResponse('DELETE ERROR: no patch id specified')

    ids = pids.split(',')
    coccis = []
    for i in ids:
        cocci = CocciReport.objects.filter(id = i)
        if len(cocci) == 0:
            logevent("DELETE: coccinelle report semantic [%s], ERROR: id %s does not exists" % (pids, i))
            return HttpResponse('DELETE ERROR: id %s does not exists' % i)
        coccis.append(cocci[0])

    for cocci in coccis:
        rtypes = Type.objects.filter(id = cocci.id + 10000)
        if len(rtypes) != 0:
            rtype = rtypes[0]

            # delete patchs owner by this type
            patchs = Report.objects.filter(type = rtype)
            for patch in patchs:
                tag = patch.tag
                patch.delete()
                tag.total -= 1
                tag.save()

            # delete except files owner by this type
            efiles = ExceptFile.objects.filter(type = rtype)
            for efile in efiles:
                efile.delete()

            rtype.delete()
        if os.path.exists(cocci.fullpath()):
            os.unlink(cocci.fullpath())
        cocci.delete()

    logevent("DELETE: coccinelle report semantic [%s], SUCCEED" % pids, True)
    return HttpResponse('DELETE SUCCEED: engine ids [%s]' % pids)

@login_required
@csrf_exempt
def report_semantic_edit(request, cocci_id):
    if request.method == "POST":
        name = get_request_paramter(request, 'name')
        title = get_request_paramter(request, 'title')
        desc = get_request_paramter(request, 'desc')
        content = get_request_paramter(request, 'content')
        options = get_request_paramter(request, 'options')

        if name is None or len(name) == 0:
            logevent("EDIT: coccinelle report semantic, ERROR: no name specified")
            return HttpResponse('EDIT ERROR: no semantic name specified')
    
        if title is None or len(title) == 0:
            logevent("EDIT: coccinelle report semantic, ERROR: no title specified")
            return HttpResponse('EDIT ERROR: no semantic title specified')
    
        if desc is None or len(desc) == 0:
            logevent("EDIT: coccinelle report semantic, ERROR: no desc specified")
            return HttpResponse('EDIT ERROR: no semantic desc specified')
    
        if content is None or len(content) == 0:
            logevent("EDIT: coccinelle report semantic, ERROR: no content specified")
            return HttpResponse('EDIT ERROR: no semantic content specified')

        if options is None:
            options = ''

        coccis = CocciReport.objects.filter(id = cocci_id)
        if len(coccis) == 0:
            logevent("EDIT: coccinelle report semantic, ERROR: id %s does not exists" % cocci_id)
            return HttpResponse('EDIT ERROR: semantic id %s does not exists' % cocci_id)

        engine = coccis[0]
        ofname = engine.fullpath()
        fname = '%s.cocci' % name.strip()
        engine.file = fname
        engine.content = content
        engine.options = options.strip()

        rtype = Type.objects.get(id = engine.id + 10000)

        einfo = []
        for efile in ExceptFile.objects.filter(type = rtype):
            einfo.append({'file': efile.file, 'reason': efile.reason})

        spctx = engine.rawformat(title, desc, einfo)
        try:
            cocci = open(engine.fullpath(), "w")
            cocci.write(spctx)
            cocci.close()
            if ofname != engine.fullpath() and os.path.exists(ofname):
                os.unlink(ofname)
        except:
            logevent("EDIT: coccinelle report semantic, ERROR: can not write file %s" % engine.fullpath())
            return HttpResponse('EDIT ERROR: can not write file %s' % engine.fullpath())

        engine.save()
    
        rtype.name = name
        rtype.ptitle = title
        rtype.pdesc = desc
        rtype.save()

        logevent("EDIT: coccinelle report semantic, SUCCEED: type id %s" % rtype.id, True)
        return HttpResponse('EDIT: coccinelle semantic, SUCCEED: type id %s' % cocci_id)
    else:
        coccis = CocciReport.objects.filter(id = cocci_id)
        if len(coccis) == 0:
            engine = None
            rtype = None
        else:
            engine = coccis[0]
            rtype = Type.objects.get(id = engine.id + 10000)
        context = RequestContext(request)
        context['cocci'] = engine
        context['type'] = rtype
        return render_to_response("engine/semanticedit.html", context)

def report_semantic_detail(request, cocci_id):
    coccis = CocciReport.objects.filter(id = cocci_id)
    if len(coccis) == 0:
        return ""
    cocci = coccis[0]
    try:
        cfile = open(cocci.fullpath(), 'r')
        content = cfile.read()
        cfile.close()
    except:
        content = cocci.content
    context = RequestContext(request)
    context['content'] = content
    return render_to_response("engine/coccidetail.html", context)

@login_required
@csrf_exempt
def report_semantic_import(request):
    fp = request.FILES['file']
    if fp != None:
        if os.path.splitext(fp.name)[1] == ".cocci":
            fname = os.path.join('/tmp', fp.name)
        else:
            fname = tempfile.mktemp()

        with open(fname, 'w+') as destination:
            for chunk in fp.chunks():
                destination.write(chunk)

        args = '/usr/dpatch/bin/importreport.sh %s' % fname
        shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
        shellOut = shelllog.communicate()[0]

        if os.path.exists(fname):
            os.unlink(fname)

        logevent("IMPORT: coccinelle semantic report, SUCCEED", True)
        return HttpResponse(shellOut)
    else:
        return HttpResponse('IMPORT ERROR: no file found')

def rewrite_report_engine(cocci):
    rtypes = Type.objects.filter(id = cocci.id + 10000)
    if len(rtypes) != 0:
        rtype = rtypes[0]

        einfo = []
        for efile in ExceptFile.objects.filter(type = rtype):
            einfo.append({'file': efile.file, 'reason': efile.reason})

        if len(einfo) > 0:
            spctx = cocci.rawformat(rtype.ptitle, rtype.pdesc, einfo)
            try:
                cocci = open(cocci.fullpath(), "w")
                cocci.write(spctx)
                cocci.close()
            except:
                pass

def report_semantic_export(request):
    cids = get_request_paramter(request, 'ids')
    if cids is None:
        return HttpResponse('EXPORT ERROR: no patch id specified')

    files = []
    for cid in cids.split(','):
        cocci = CocciReport.objects.filter(id = cid)
        if len(cocci) == 0:
            logevent("EXPORT: coccinelle semantic [%s], ERROR: id %s does not exists" % (cids, cid))
            return HttpResponse('EXPORT ERROR: id %s does not exists' % cid)
        rewrite_report_engine(cocci[0])
        files.append(cocci[0].fullpath())

    response = HttpResponse(mimetype='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename=cocci-reports-%s.tar.gz' % strftime("%Y%m%d%H%M%S", gmtime())
    archive = tarfile.open(fileobj=response, mode='w:gz')

    for fname in files:
        if os.path.exists(fname):
            archive.add(fname, arcname = os.path.basename(fname))

    archive.close()

    logevent("EXPORT: coccinelle report semantic [%s], SUCCEED" % (cids), True)
    return response

def report_semantic_export_all(request):
    files = []
    for cocci in CocciReport.objects.all():
        rewrite_report_engine(cocci)
        files.append(cocci.fullpath())

    response = HttpResponse(mimetype='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename=cocci-reports-all-%s.tar.gz' % strftime("%Y%m%d%H%M%S", gmtime())
    archive = tarfile.open(fileobj=response, mode='w:gz')

    for fname in files:
        if os.path.exists(fname):
            archive.add(fname, arcname = os.path.basename(fname))

    archive.close()

    logevent("EXPORT: coccinelle report semantic all, SUCCEED", True)
    return response
