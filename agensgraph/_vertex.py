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
from psycopg2.extras import json

from agensgraph._graphid import cast_graphid

_pattern = re.compile(r'(.+?)\[(.+?)\](.*)', re.S)

class Vertex(object):
    def __init__(self, label, vid, props):
        self.label = label
        self.vid = vid
        self.props = props

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.vid == other.vid
        return False

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self)

    def __str__(self):
        return "%s[%s]%s" % (self.label, self.vid, json.dumps(self.props))

def cast_vertex(value, cur):
    if value is None:
        return None

    m = _pattern.match(value)
    if m:
        label = m.group(1)
        vid = cast_graphid(m.group(2), cur)
        props = json.loads(m.group(3))
        return Vertex(label, vid, props)
    else:
        raise InterfaceError("bad vertex representation: %s" % value)
