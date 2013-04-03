#!/bin/sh
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

BIN_DIR=`dirname $0`
DAILYPATCH_BASE=`readlink -e $BIN_DIR/../`

PYTHONPATH="$DAILYPATCH_BASE/" \
        DJANGO_SETTINGS_MODULE=dpatch.settings \
        "$DAILYPATCH_BASE/bin/dailypatch.py"

PYTHONPATH="$DAILYPATCH_BASE/" \
        DJANGO_SETTINGS_MODULE=dpatch.settings \
        "$DAILYPATCH_BASE/bin/dailyreport.py"

PYTHONPATH="$DAILYPATCH_BASE/" \
        DJANGO_SETTINGS_MODULE=dpatch.settings \
        "$DAILYPATCH_BASE/bin/dailystatus.py"

PYTHONPATH="$DAILYPATCH_BASE/" \
        DJANGO_SETTINGS_MODULE=dpatch.settings \
        "$DAILYPATCH_BASE/bin/dailybuild.py"

exit 0