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

from agensgraph._graphpath import Path, cast_graphpath

class TestPath(unittest.TestCase):
    def setUp(self):
        self.o0 = '[n[7.3]{}]'
        self.p0 = cast_graphpath(self.o0, None)
        self.o1 = '[n[7.3]{},r[5.7][7.3,7.9]{},n[7.9]{}]'
        self.p1 = cast_graphpath(self.o1, None)

    def test_vertices(self):
        self.assertEqual(1, len(self.p0.vertices))
        self.assertEqual('n[7.3]{}', str(self.p0.vertices[0]))
        self.assertEqual(2, len(self.p1.vertices))
        self.assertEqual('n[7.3]{}', str(self.p1.vertices[0]))
        self.assertEqual('n[7.9]{}', str(self.p1.vertices[1]))

    def test_edges(self):
        self.assertEqual(0, len(self.p0.edges))
        self.assertEqual(1, len(self.p1.edges))
        self.assertEqual('r[5.7][7.3,7.9]{}', str(self.p1.edges[0]))

    def test_eq(self):
        self.assertEqual(self.p0, self.p0)
        self.assertEqual(self.p1, self.p1)

    def test_len(self):
        self.assertEqual(0, len(self.p0))
        self.assertEqual(1, len(self.p1))

    def test_str(self):
        self.assertEqual(self.o0, str(self.p0))
        self.assertEqual(self.o1, str(self.p1))

    def test_repr(self):
        self.assertEqual("%s(%s)" % (Path.__name__, self.p0), repr(self.p0))
        self.assertEqual("%s(%s)" % (Path.__name__, self.p1), repr(self.p1))
