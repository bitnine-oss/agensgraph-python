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

from agensgraph._graphid import GraphId, cast_graphid, adapt_graphid

class TestGraphId(unittest.TestCase):
    def setUp(self):
        self.out = '7.9'
        self.gid = cast_graphid(self.out, None)

    def test_getId(self):
        self.assertEqual((7, 9), self.gid.getId())

    def test_eq(self):
        self.assertEqual(self.gid, self.gid)

    def test_str(self):
        self.assertEqual(self.out, str(self.gid))

    def test_repr(self):
        self.assertEqual("%s(%s)" % (GraphId.__name__, self.gid),
                         repr(self.gid))

    def test_adapt(self):
        self.assertEqual(b"'7.9'", adapt_graphid(self.gid).getquoted())
