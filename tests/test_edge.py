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

from agensgraph._edge import Edge, cast_edge
from agensgraph._graphid import GraphId

class TestEdge(unittest.TestCase):
    def setUp(self):
        out = 'e[5.7][7.3,7.9]{"s": "", "i": 0, "b": false, "a": [], "o": {}}'
        self.e = cast_edge(out, None)

    def test_label(self):
        self.assertEqual('e', self.e.label)

    def test_eid(self):
        self.assertEqual(GraphId((5, 7)), self.e.eid)

    def test_start(self):
        self.assertEqual(GraphId((7, 3)), self.e.start)

    def test_end(self):
        self.assertEqual(GraphId((7, 9)), self.e.end)

    def test_props(self):
        self.assertEqual('', self.e.props['s'])
        self.assertEqual(0, self.e.props['i'])
        self.assertFalse(self.e.props['b'])
        self.assertEqual([], self.e.props['a'])
        self.assertEqual({}, self.e.props['o'])

    def test_eq(self):
        self.assertEqual(self.e, self.e)

    def test_str(self):
        props = '{"s": "", "i": 0, "b": false, "a": [], "o": {}}'
        out = "e[5.7][7.3,7.9]%s" % json.dumps(json.loads(props))
        self.assertEqual(out, str(self.e))

    def test_repr(self):
        self.assertEqual("%s(%s)" % (Edge.__name__, self.e), repr(self.e))
