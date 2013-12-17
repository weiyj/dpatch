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

from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib.auth import views as auth_views

htdocs = os.path.join(settings.ROOT_DIR, 'htdocs')

urlpatterns = patterns('',
    url(r'^javascripts/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(htdocs, 'javascripts')}),
    url(r'^images/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(htdocs, 'images')}),
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(htdocs, 'css')}),

    # login/logout
    url(r'^user/login/$', auth_views.login,
        {'template_name': 'login.html'},
        name = 'auth_login'),
    url(r'^user/logout/$', auth_views.logout,
        {'next_page': '/'},
        name = 'auth_logout'),
)

urlpatterns += patterns('dpatch.views.base',
    url(r'^$', 'patchstatus'),
    url(r'^dashboard/$', 'dashboard'),
    url(r'^patchstatus/$', 'patchstatus'),
    url(r'^reportstatus/$', 'reportstatus'),
    url(r'^patchengine/$', 'patchengine'),
    url(r'^administration/$', 'administration'),
    url(r'^help/$', 'helppage'),
)

urlpatterns += patterns('dpatch.views.patch',
    url(r'^patch/list/(?P<tag_name>[^/]*)/data/$', 'patchlistdata'),
    url(r'^patch/list/like/(?P<tag_name>[^/]*)/$', 'patch_list_version'),
    url(r'^patch/list/(?P<tag_name>[^/]*)/$', 'patchlist'),
    url(r'^patch/(?P<patch_id>\d+)/$', 'showpatch'),
    url(r'^patch/raw/(?P<patch_id>\d+)/$', 'patch_raw'),
    url(r'^patch/merge/$', 'patchlistmerge'),
    url(r'^patch/unmerge/$', 'patchunmerge'),
    url(r'^patch/delete/$', 'patchdelete'),
    url(r'^patch/export/$', 'patch_export'),
    url(r'^patch/export/all/(?P<tag_name>[^/]*)/$', 'patch_export_all'),
    url(r'^patch/edit/(?P<patch_id>\d+)/$', 'patchedit'),
    url(r'^patch/edit/(?P<patch_id>\d+)/save/$', 'patcheditsave'),
    url(r'^patch/review/(?P<patch_id>\d+)/$', 'patchreview'),
    url(r'^patch/send/wizard/(?P<patch_id>\d+)/$', 'patchsendwizard'),
    url(r'^patch/send/wizard/(?P<patch_id>\d+)/step/$', 'patchsendwizardstep'),
    url(r'^patch/build/(?P<patch_id>\d+)/$', 'patch_build'),
    url(r'^patch/fileinfo/(?P<patch_id>\d+)$', 'patch_fileinfo'),
    url(r'^patch/fix/(?P<patch_id>\d+)/$', 'patch_fix'),
    url(r'^patch/new/$', 'patch_new'),
    url(r'^patch/status/$', 'patch_status'),
    url(r'^patch/build/all/$', 'patch_build_all'),
    url(r'^patch/build/status/$', 'patch_build_status'),
    url(r'^patch/special/$', 'patch_special'),
    url(r'^patch/stable/$', 'patch_stable'),
    url(r'^patch/fetch/(?P<patch_id>\d+)/$', 'patch_fetch_commit'),
)

urlpatterns += patterns('dpatch.views.report',
    url(r'^report/list/(?P<tag_name>[^/]*)/$', 'report_list'),
    url(r'^report/list/like/(?P<tag_name>[^/]*)/$', 'report_list_version'),
    url(r'^report/list/(?P<tag_name>[^/]*)/data/$', 'report_list_data'),
    url(r'^report/delete/$', 'report_delete'),
    url(r'^report/detail/(?P<report_id>\d+)/$', 'report_detail'),
    url(r'^report/patch/(?P<report_id>\d+)/$', 'report_patch'),
    url(r'^report/fix/(?P<report_id>\d+)/$', 'report_fix'),
    url(r'^report/new/$', 'report_new'),
    url(r'^report/edit/(?P<report_id>\d+)/$', 'report_edit'),
    url(r'^report/merge/$', 'report_merge'),
    url(r'^report/unmerge/$', 'report_unmerge'),
    url(r'^report/export/$', 'report_export'),
    url(r'^report/export/all/(?P<tag_name>[^/]*)/$', 'report_export_all'),
    url(r'^report/send/wizard/(?P<report_id>\d+)/$', 'report_sendwizard'),
    url(r'^report/send/wizard/(?P<report_id>\d+)/step/$', 'report_sendwizard_step'),
    url(r'^report/build/(?P<report_id>\d+)/$', 'report_build'),
    url(r'^report/fileinfo/(?P<report_id>\d+)$', 'report_fileinfo'),
    url(r'^report/status/$', 'report_status'),
    url(r'^report/build/status/$', 'report_build_status'),
    url(r'^report/build/all/$', 'report_build_all'),
    url(r'^report/special/$', 'report_special'),
    url(r'^report/stable/$', 'report_stable'),
    url(r'^report/fetch/(?P<report_id>\d+)/$', 'report_fetch_commit'),
)

urlpatterns += patterns('dpatch.views.engine',
    url(r'^engine/cocci/semantic/$', 'semantic'),
    url(r'^engine/cocci/list/$', 'semantic_list'),
    url(r'^engine/cocci/edit/(?P<cocci_id>\d+)/$', 'semantic_edit'),
    url(r'^engine/cocci/detail/(?P<cocci_id>\d+)/$', 'semantic_detail'),
    url(r'^engine/cocci/new/$', 'semantic_new'),
    url(r'^engine/cocci/delete/$', 'semantic_delete'),
    url(r'^engine/cocci/import/$', 'semantic_import'),
    url(r'^engine/cocci/export/$', 'semantic_export'),
    url(r'^engine/cocci/export/all/$', 'semantic_export_all'),
    url(r'^engine/cocci/deltascan/$', 'semantic_deltascan'),
    url(r'^engine/cocci/fullscan/$', 'semantic_fullscan'),
    url(r'^engine/cocci/move/$', 'semantic_move_to_report'),
    url(r'^engine/type/(?P<type_id>\d+)/enable/$', 'enabletype'),
    url(r'^engine/type/(?P<type_id>\d+)/switchtype/$', 'engine_switch_type'),

    url(r'^engine/cocci/report/$', 'report_semantic'),
    url(r'^engine/cocci/report/list/$', 'report_semantic_list'),
    url(r'^engine/cocci/report/new/$', 'report_semantic_new'),
    url(r'^engine/cocci/report/delete/$', 'report_semantic_delete'),
    url(r'^engine/cocci/report/edit/(?P<cocci_id>\d+)/$', 'report_semantic_edit'),
    url(r'^engine/cocci/report/detail/(?P<cocci_id>\d+)/$', 'report_semantic_detail'),
    url(r'^engine/cocci/report/import/$', 'report_semantic_import'),
    url(r'^engine/cocci/report/export/$', 'report_semantic_export'),
    url(r'^engine/cocci/report/export/all/$', 'report_semantic_export_all'),
    url(r'^engine/cocci/report/deltascan/$', 'report_semantic_deltascan'),
    url(r'^engine/cocci/report/fullscan/$', 'report_semantic_fullscan'),

    url(r'^engine/exceptfile/$', 'exceptfile'),
    url(r'^engine/exceptfile/list/$', 'exceptfile_list'),
    url(r'^engine/exceptfile/new/$', 'exceptfile_new'),
    url(r'^engine/exceptfile/delete/$', 'exceptfile_delete'),
)

urlpatterns += patterns('dpatch.views.event',
    url(r'^event/logs/$', 'logs'),
    url(r'^event/logs/data/$', 'log_data'),
    url(r'^event/logs/detail/(?P<log_id>\d+)/$', 'log_detail'),
    url(r'^event/logs/delete/$', 'log_delete'),
    url(r'^event/events/$', 'events'),
    url(r'^event/events/data/$', 'event_data'),
    url(r'^event/events/delete/$', 'event_delete'),
)

urlpatterns += patterns('dpatch.views.admin',
    url(r'^sysadmin/gitrepo/$', 'gitrepo'),
    url(r'^sysadmin/gitrepo/list/$', 'gitrepolist'),
    url(r'^sysadmin/gitrepo/add/$', 'gitrepoadd'),
    url(r'^sysadmin/gitrepo/edit/(?P<repo_id>\d+)/$', 'git_repo_edit'),
    url(r'^sysadmin/gitrepo/delete/$', 'gitrepodelete'),
    url(r'^sysadmin/gitrepo/enable/(?P<repo_id>\d+)/$', 'git_repo_enable'),
    url(r'^sysadmin/gitrepo/enable/build/(?P<repo_id>\d+)/$', 'git_repo_enable_build'),

    url(r'^sysadmin/gitemail/$', 'git_email'),
    url(r'^sysadmin/gitemail/test/$', 'git_email_test'),

    url(r'^sysadmin/sysconfig/$', 'sys_config'),
    url(r'^sysadmin/sysconfig/list/$', 'sys_config_list'),
)

urlpatterns += patterns('dpatch.views.dash',
    url(r'^dashboard/status/(?P<repo_id>\d+)/$', 'patch_status'),
    url(r'^dashboard/patch/types/(?P<repo_id>\d+)/$', 'patch_by_type'),
    url(r'^dashboard/patch/tags/(?P<repo_id>\d+)/$', 'patch_by_tag'),
    url(r'^dashboard/patch/daily/(?P<repo_id>\d+)/$', 'patch_by_daily'),
)
