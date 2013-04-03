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

from dpatch.models import Module

def register_module_name(fname, oldmodule, newmodule):
    if len(oldmodule) == 0 or len(newmodule) == 0 or oldmodule == newmodule:
        return

    mnames = Module.objects.filter(file = fname)
    if len(mnames) == 0:
        mname = Module(file = fname, name = newmodule)
        mname.save()
    else:
        for mname in mnames:
            mname.name = newmodule
            mname.save()