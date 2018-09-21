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

import unittest

from psycopg2.extras import json

from agensgraph._graphid import GraphId
from agensgraph._vertex import Vertex, cast_vertex

class TestVertex(unittest.TestCase):
    def setUp(self):
        out = 'v[7.9]{"s": "", "i": 0, "b": false, "a": [], "o": {}}'
        self.v = cast_vertex(out, None)

    def test_label(self):
        self.assertEqual('v', self.v.label)

    def test_vid(self):
        self.assertEqual(GraphId((7, 9)), self.v.vid)

    def test_props(self):
        self.assertEqual('', self.v.props['s'])
        self.assertEqual(0, self.v.props['i'])
        self.assertFalse(self.v.props['b'])
        self.assertEqual([], self.v.props['a'])
        self.assertEqual({}, self.v.props['o'])

    def test_eq(self):
        self.assertEqual(self.v, self.v)

    def test_str(self):
        props = '{"s": "", "i": 0, "b": false, "a": [], "o": {}}'
        out = "v[7.9]%s" % json.dumps(json.loads(props))
        self.assertEqual(out, str(self.v))

    def test_repr(self):
        self.assertEqual("%s(%s)" % (Vertex.__name__, self.v), repr(self.v))
