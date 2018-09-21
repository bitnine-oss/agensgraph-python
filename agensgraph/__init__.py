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

from psycopg2 import extensions as _ext

from agensgraph._graphid import (
    GraphId, cast_graphid as _cast_graphid, adapt_graphid as _adapt_graphid)
from agensgraph._vertex import Vertex, cast_vertex as _cast_vertex
from agensgraph._edge import Edge, cast_edge as _cast_edge
from agensgraph._graphpath import Path, cast_graphpath as _cast_graphpath
from agensgraph._property import Property

_GRAPHID_OID = 7002
_VERTEX_OID = 7012
_EDGE_OID = 7022
_GRAPHPATH_OID = 7032

GRAPHID = _ext.new_type((_GRAPHID_OID,), 'GRAPHID', _cast_graphid)
_ext.register_type(GRAPHID)
_ext.register_adapter(GraphId, _adapt_graphid)

VERTEX = _ext.new_type((_VERTEX_OID,), 'VERTEX', _cast_vertex)
_ext.register_type(VERTEX)

EDGE = _ext.new_type((_EDGE_OID,), 'EDGE', _cast_edge)
_ext.register_type(EDGE)

PATH = _ext.new_type((_GRAPHPATH_OID,), 'PATH', _cast_graphpath)
_ext.register_type(PATH)

__all__ = ['GraphId', 'Vertex', 'Edge', 'Path', 'Property',
           'GRAPHID', 'VERTEX', 'EDGE', 'PATH']
