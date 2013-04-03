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

from dpatch.models import SysConfig

def read_config(name, default = None):
    configs = SysConfig.objects.filter(name = name)
    if len(configs) == 0:
        return default
    config = configs[0]
    if default is None:
        return config.value
    elif isinstance(default, basestring):
        return config.value
    elif isinstance(default, bool):
        return config.value in ['True', 'Yes']
    elif isinstance(default, int):
        return int(config.value)
    else:
        return config.value

def write_config(name, value):
    configs = SysConfig.objects.filter(name = name)
    if len(configs) == 0:
        config = SysConfig(name = name, value = str(value))
        config.save()
    else:
        config = configs[0]
        config.value = str(value)
        config.save()