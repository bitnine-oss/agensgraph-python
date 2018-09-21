'''
Copyright (c) 2014-2018 Bitnine, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import re

from psycopg2 import InterfaceError
from psycopg2.extensions import AsIs

_pattern = re.compile(r'(\d+)\.(\d+)')

class GraphId(object):
    def __init__(self, gid):
        self.gid = gid

    def getId(self):
        return self.gid

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.gid == other.gid
        return False

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self)

    def __str__(self):
        return "%d.%d" % self.gid

def cast_graphid(value, cur):
    if value is None:
        return None

    m = _pattern.match(value)
    if m:
        labid = int(m.group(1))
        locid = int(m.group(2))
        gid = (labid, locid)
        return GraphId(gid)
    else:
        raise InterfaceError("bad graphid representation: %s" % value)

def adapt_graphid(graphid):
    return AsIs("'%s'" % graphid)
