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

from agensgraph._property import Property

from psycopg2.extensions import QuotedString, adapt

class TestProperty(unittest.TestCase):
    def test_string(self):
        self.assertEqual(r"'\"'", Property('"').getquoted())
        self.assertEqual(r"''''", Property("'").getquoted())

    def test_number(self):
        self.assertEqual('0', Property(0).getquoted())
        self.assertEqual('-1', Property(-1).getquoted())
        self.assertEqual('3.14159', Property(3.14159).getquoted())

    def test_boolean(self):
        self.assertEqual('true', Property(True).getquoted())
        self.assertEqual('false', Property(False).getquoted())

    def test_null(self):
        self.assertEqual('null', Property(None).getquoted())

    def test_array(self):
        a = ["'\\\"'", 3.14159, True, None, (), {}]
        e = "['''\\\\\\\"''',3.14159,true,null,[],{}]"
        self.assertEqual(e, Property(a).getquoted())

    def test_object(self):
        self.assertEqual("{'\\\"':'\\\"'}", Property({'"': '"'}).getquoted())
        self.assertEqual("{'3.14159':3.14159}",
                         Property({3.14159: 3.14159}).getquoted())
        self.assertEqual("{'true':false}", Property({True: False}).getquoted())
        self.assertEqual("{'null':null}", Property({None: None}).getquoted())
        self.assertEqual("{'a':[]}", Property({'a': []}).getquoted())
        self.assertEqual("{'o':{}}", Property({'o': {}}).getquoted())
        self.assertRaises(TypeError, Property({(): None}).getquoted)
