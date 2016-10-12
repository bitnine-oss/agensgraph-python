'''
Copyright (c) 2014-2016, Bitnine Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import re, json

_v_matcher = re.compile(r'(.+)\[(\d+)\.(\d+)\](.+)')
_e_matcher = re.compile(r'(.+)\[(\d+)\.(\d+)\]\[(\d+)\.(\d+),(\d+)\.(\d+)\](.*)')

class GID:
    def __init__(self, oident, ident):
        self.oid = oident
        self.id = ident
    def __repr__(self):
        return "[" + self.oid + "." + self.id + "]"

class Vertex:
    def __init__(self, value):
        m = _v_matcher.match(value)
        if m == None:
            return ValueError
        self.label = m.group(1)
        self.vid = GID(m.group(2), m.group(3))
        self.props = json.loads(m.group(4))
    def __repr__(self):
        return self.label + str(self.vid) + json.dumps(self.props)

def _cast_vertex(value, cur):
    if value is None:
        return None
    try:
        v = Vertex(value)
    except:
        return psycopg2.InterfaceError("bad vertex representation: %s" % value)
    return v

class Edge:
    def __init__(self, value):
        m = _e_matcher.match(value)
        if m == None:
            raise ValueError
        self.label = m.group(1)
        self.eid = GID(m.group(2), m.group(3))
        self.svid = GID(m.group(4), m.group(5))
        self.evid = GID(m.group(6), m.group(7))
        self.props = json.loads(m.group(8))
    def __repr__(self):
        svid = str(self.svid)[0:-1]
        evid = str(self.evid)[1:]
        return self.label + str(self.eid) + svid + ',' + evid + json.dumps(self.props)

def _cast_edge(value, cur):
    if value is None:
        return None
    try:
        e = Edge(value)
    except:
        return psycopg2.InterfaceError("bad edge representation: %s" % value)
    return e

class Path:
    def __init__(self, value):
        l = self._tokenize(value)
        if l == None:
            raise ValueError
        self.vertices = map(Vertex, l[0::2])
        self.edges = map(Edge, l[1::2])
    def _tokenize(self, value):
        i = 0
        s = 0
        depth = 0
        inGID = False
        l = []
        v = value[1:-1] # remove '[' and ']'
        for c in v:
            if '{' == c:
                depth += 1
            elif '}' == c:
                depth -= 1
            elif 0 == depth and '[' == c: # for GID
                inGID = True
            elif inGID and ']' == c:
                inGID = False
            elif 0 == depth and False == inGID and ',' == c:
                l.append(v[s:i])
                s = i + 1
            if depth < 0:
                raise ValueError
            i += 1
        l.append(v[s:i])
        return l
    def __repr__(self):
        return ''.join(map(lambda x,y:repr(x)+repr(y),self.vertices,self.edges))[0:-4]
    def start(self):
        return self.vertices[0]
    def end(self):
        return self.vertices[-1]
    def len(self):
        return len(self.edges)

def _cast_path(value, cur):
    if value is None:
        return None
    try:
        p = Path(value)
    except:
        return psycopg2.InterfaceError("bad path representation: %s" % value)
    return p

import psycopg2

VERTEX = psycopg2.extensions.new_type((7012,), "VERTEX", _cast_vertex)
psycopg2.extensions.register_type(VERTEX)

EDGE = psycopg2.extensions.new_type((7022,), "EDGE", _cast_edge)
psycopg2.extensions.register_type(EDGE)

PATH = psycopg2.extensions.new_type((7032,), "PATH", _cast_path)
psycopg2.extensions.register_type(PATH)

class AgProp(psycopg2.extras.Json):
    def getquoted(self):
        return psycopg2.extras.Json.getquoted(self) + '::jsonb'

