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

import unittest
import psycopg2
from psycopg2.extras import Json
import agtype

class BasicTest(unittest.TestCase):
    def setUp(self):
        self.conn = psycopg2.connect("dbname=test user=postgres")
        self.cur = self.conn.cursor()
        try:
            self.cur.execute("drop graph p cascade")
        except:
            self.conn.commit()
        self.cur.execute("create graph p")
        self.cur.execute("set graph_path = p")
        self.conn.commit()
    def tearDown(self):
        self.conn.commit()
        self.cur.execute("drop graph p cascade")
        self.cur.close()
        self.conn.close()

class CreateTest(BasicTest):
    def setUp(self):
        BasicTest.setUp(self)
        self.cur.execute("create vlabel person")
        self.cur.execute("create vlabel company")
        self.cur.execute("create elabel employee")
    def test_CreateWithBind(self):
        self.cur.execute(
                "CREATE ( :person { 'name': 'XXX', 'from': 'Sweden', 'klout': %s } )", (99,))
        self.cur.execute("MATCH (n:person {'name': %s}) return n", ('XXX',))
        n = self.cur.fetchone()[0]
        self.assertEquals(99, n.props["klout"])
    def test_CreateWithBindPrimitiveProp(self):
        with self.assertRaises(psycopg2.ProgrammingError):
            self.cur.execute("CREATE ( :person %s )", (Json(10),));
    def test_CreateWithBindWholeProp(self):
        self.cur.execute("CREATE ( :person %s )", 
                (Json({'name': 'ktlee', 'from': 'Korea', 'klout': 17}),))
        self.cur.execute("MATCH (n:person {'name': %s}) return n", ('ktlee',))
        n = self.cur.fetchone()[0]
        self.assertEquals(17, n.props["klout"])

class LabelInheritTest(BasicTest):
    def setUp(self):
        BasicTest.setUp(self)
        self.cur.execute("create vlabel parent")
        self.cur.execute("create vlabel child inherits (parent)")
        self.cur.execute("create (:parent {'name': 'father'})")
        self.cur.execute("create (:child {'name': 'son'})")
        pass
    def test_MultiLable(self):
        self.cur.execute("MATCH (x:parent) RETURN x ORDER BY x.name")
        x = self.cur.fetchone()[0]
        self.assertEquals("father", x.props["name"])
        x = self.cur.fetchone()[0]
        self.assertEquals("son", x.props["name"])
        self.cur.execute("MATCH (x:child) RETURN x")
        x = self.cur.fetchone()[0]
        self.assertEquals("son", x.props["name"])

class MatchTest(BasicTest):
    def setUp(self):
        BasicTest.setUp(self)
        self.cur.execute("create vlabel company")
        self.cur.execute("create vlabel person")
        self.cur.execute("create elabel employee")
        self.cur.execute("create elabel manage")
        self.cur.execute("create (:company {'name': 'bitnine'})"
                + "-[:employee]"
                + "->(:person {'name': 'kskim'})"
                + "-[:manage]"
                + "->(:person {'name': 'ktlee'})");
        self.cur.execute("create (c:company {'name': 'bitnine'}) "
                + "create (c)-[:employee]"
                + "->(:person {'name': 'jsyang'})")
        self.cur.execute("create (c:company {'name': 'bitnine'}) "
                + ", (p:person {'name': 'ktlee'}) "
                + "create (c)-[:employee]->(p)")
        self.cur.execute("match (m:person {'name': 'kskim'})"
                + ", (p:person {'name': 'jsyang'}) "
                + "create (m)-[:manage]->(p)")
    def test_Match(self):
        self.cur.execute("MATCH (c)-[e]->(p1)-[m]->(p2) RETURN p1, p2 ORDER BY p2.name")
        row = self.cur.fetchone()
        boss = row[0]
        self.assertEquals("person", boss.label)
        self.assertEquals("kskim", boss.props["name"])
        member = row[1]
        self.assertEquals("jsyang", member.props["name"])
        row = self.cur.fetchone()
        boss = row[0]
        self.assertEquals("person", boss.label)
        self.assertEquals("kskim", boss.props["name"])
        member = row[1]
        self.assertEquals("ktlee", member.props["name"])
    def test_Path(self):
        self.cur.execute("MATCH p=()-[]->()-[]->({'name':'ktlee'}) RETURN p")
        p = self.cur.fetchone()[0]
        self.assertEquals(["bitnine","kskim","ktlee"], 
                [v.props["name"] for v in p.vertices])
        self.assertEquals(["employee","manage"],
                [e.label for e in p.edges])
        self.assertEquals(2, p.len())

class PropertyTest(BasicTest):
    def setUp(self):
        BasicTest.setUp(self)
        self.cur.execute("create vlabel company")
        self.cur.execute("create vlabel person")
        self.cur.execute("create elabel employee")
        self.cur.execute("create (:company {'name':'bitnine'})"
                + "-[:employee {'no':1}]"
                + "->(:person {'name':'jsyang', 'age':20, 'height':178.5, 'married':false})")
        self.cur.execute("match (:company {'name':'bitnine'})"
                + "create (c)-[:employee {'no':2}]"
                + "->(:person '{\"name\":\"ktlee\", \"hobbies\":[\"reading\", \"climbing\"], \"age\":null}')")
        self.cur.execute("create (:person {'name': 'Emil', 'from': 'Sweden', 'klout': 99})")
    def test_Property(self):
        self.cur.execute("match (n)-[:employee {'no':1}]->(m) RETURN n, m")
        row = self.cur.fetchone()
        self.assertEquals(20, row[1].props["age"])
        self.assertEquals(178.5, row[1].props["height"])
        self.assertFalse(row[1].props["married"])
        self.cur.execute("match (n)-[:employee {'no':2}]->(m) RETURN n, m")
        row = self.cur.fetchone()
        self.assertEquals("climbing", row[1].props["hobbies"][1])
        self.cur.execute("match (n)-[{'no':2}]->(m) return m.hobbies::jsonb as hobbies")
        hobbies = self.cur.fetchone()[0]
        self.assertEquals("reading", hobbies[0])
        self.cur.execute("match (ee:person) where ee.klout::int = 99 "
                + "return ee.name, to_jsonb(ee.name)")
        row = self.cur.fetchone()
        self.assertIsInstance(row[0], str)
        self.assertEquals("Emil", row[0])
        self.assertIsInstance(row[1], unicode)
        self.assertEquals('Emil', row[1])

class ReturnTest(BasicTest):
    def test_Return(self):
        self.cur.execute("RETURN 'be' || ' happy!', 1+1")
        row = self.cur.fetchone()
        self.assertEquals("be happy!", row[0])
        self.assertEquals(2, row[1])
        self.cur.execute("RETURN %s", (Json({'name': 'Emil'}),))
        row = self.cur.fetchone()[0]
        #self.assertEquals("\"Emil\"", row["name"])

class WhereTest(BasicTest):
    def setUp(self):
        BasicTest.setUp(self)
        self.cur.execute("create vlabel person")
        self.cur.execute("create (:person { 'name': 'Emil', 'from': 'Sweden', 'klout': 99})")
    def test_Where(self):
        self.cur.execute("match (ee:person) where ee.name = 'Emil' return ee")
        row = self.cur.fetchone()[0]
        self.assertEquals(99, row.props["klout"])
        #self.cur.execute("match (ee:person) where ee.klout = to_jsonb(99::int) return ee")
        self.cur.execute("match (ee:person) where ee.klout::int = %s return ee", (99,))
        row = self.cur.fetchone()[0]
        self.assertEquals(99, row.props["klout"])
    def test_WhereBind(self):
        self.cur.execute("match (ee:person) where ee.from = %s return ee", ('Sweden',))
        row = self.cur.fetchone()[0]
        self.assertEquals(99, row.props["klout"])
        self.cur.execute("match (ee:person {'klout': %s}) return ee.name", (99,))
        row = self.cur.fetchone()[0]
        self.assertIsInstance(row, str)
        self.assertEquals("Emil", row)
    def test_WhereBindJson(self):
        self.cur.execute("match (ee:person) where ee.name = %s return ee", ("Emil",))
        row = self.cur.fetchone()[0]
        self.assertIsInstance(row, agtype.Vertex)
        self.assertEquals("Emil", row.props["name"])
    def test_MatchBindStr(self):
        self.cur.execute("match (ee:person %s) return ee", 
                ("{\"name\": \"Emil\"}",))
        row = self.cur.fetchone()[0]
        self.assertEquals(99, row.props["klout"])
    def test_MatchBindJson(self):
        self.cur.execute("match (ee:person %s) return ee", 
                (Json({'name': 'Emil'}),))
        row = self.cur.fetchone()[0]
        self.assertEquals(99, row.props["klout"])

if __name__ == '__main__':
    unittest.main()
