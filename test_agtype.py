
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

'''

import unittest
import psycopg2
import agtype

class BasicTest(unittest.TestCase):
    def setUp(self):
        self.conn = psycopg2.connect("dbname=agens user=bylee host=127.0.0.1")
        self.cur = self.conn.cursor()
        try:
            self.cur.execute("DROP GRAPH p CASCADE")
        except:
            self.conn.commit()
        self.cur.execute("CREATE GRAPH p")
        self.cur.execute("SET GRAPH_PATH = p")
        self.conn.commit()
    def tearDown(self):
        self.conn.commit()
        self.cur.execute("DROP GRAPH p CASCADE")
        self.cur.close()
        self.conn.close()

class CreateTest(BasicTest):
    def setUp(self):
        BasicTest.setUp(self)
        self.cur.execute("CREATE VLABEL person")
        self.cur.execute("CREATE VLABEL company")
        self.cur.execute("CREATE ELABEL employee")
    def test_CreateWithBind(self):
        self.cur.execute(
            "CREATE ( :person { name: 'XXX', from: 'Sweden', klout: %s } )", (99,))
        self.cur.execute("MATCH (n:person {name: %s}) RETURN n", ('XXX',))
        n = self.cur.fetchone()[0]
        self.assertEquals(99, n.props["klout"])

class LabelInheritTest(BasicTest):
    def setUp(self):
        BasicTest.setUp(self)
        self.cur.execute("CREATE VLABEL parent")
        self.cur.execute("CREATE VLABEL child INHERITS (parent)")
        self.cur.execute("CREATE (:parent {name: 'father'})")
        self.cur.execute("CREATE (:child {name: 'son'})")
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
        self.cur.execute("CREATE VLABEL company")
        self.cur.execute("CREATE VLABEL person")
        self.cur.execute("CREATE ELABEL employee")
        self.cur.execute("CREATE ELABEL manage")
        self.cur.execute("CREATE (:company {name: 'bitnine'})"
                         + "-[:employee]"
                         + "->(:person {name: 'kskim'})"
                         + "-[:manage]"
                         + "->(:person {name: 'ktlee'})");
        self.cur.execute("CREATE (c:company {name: 'bitnine'}) "
                         + "CREATE (c)-[:employee]"
                         + "->(:person {name: 'jsyang'})")
        self.cur.execute("CREATE (c:company {name: 'bitnine'}) "
                         + ", (p:person {name: 'ktlee'}) "
                         + "CREATE (c)-[:employee]->(p)")
        self.cur.execute("MATCH (m:person {name: 'kskim'})"
                         + ", (p:person {name: 'jsyang'}) "
                         + "CREATE (m)-[:manage]->(p)")
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
        self.cur.execute("MATCH p=()-[]->()-[]->({name:'ktlee'}) RETURN p")
        p = self.cur.fetchone()[0]
        self.assertEquals('company[3.1]{"name": "bitnine"},employee[5.1][3.1,4.1]{},'
                          + 'person[4.1]{"name": "kskim"},manage[6.1][4.1,4.2]{},'
                          + 'person[4.2]{"name": "ktlee"}',
                          str(p))

        self.assertEquals(["bitnine","kskim","ktlee"],
                          [v.props["name"] for v in p.vertices])
        self.assertEquals(["employee","manage"],
                          [e.label for e in p.edges])
        self.assertEquals(2, p.len())

class PropertyTest(BasicTest):
    def setUp(self):
        BasicTest.setUp(self)
        self.cur.execute("CREATE VLABEL company")
        self.cur.execute("CREATE VLABEL person")
        self.cur.execute("CREATE ELABEL employee")
        self.cur.execute("CREATE (:company {name:'bitnine'})"
                         + "-[:employee {no:1}]"
                         + "->(:person {name:'jsyang', age:20, height:178.5, married:false})")
        self.cur.execute("MATCH (:company {name:'bitnine'})"
                         + "CREATE (c)-[:employee {no:2}]"
                         + "->(:person {\"name\":\'ktlee\', \"hobbies\":[\'reading\', \'climbing\'], \"age\":null})")
        self.cur.execute("CREATE (:person {name: 'Emil', from: 'Sweden', klout: 99})")
    def test_Property(self):
        self.cur.execute("MATCH (n)-[:employee {no:1}]->(m) RETURN n, m")
        row = self.cur.fetchone()
        self.assertEquals(20, row[1].props["age"])
        self.assertEquals(178.5, row[1].props["height"])
        self.assertFalse(row[1].props["married"])
        self.cur.execute("MATCH (n)-[:employee {no:2}]->(m) RETURN n, m")
        row = self.cur.fetchone()
        self.assertEquals("climbing", row[1].props["hobbies"][1])
        self.cur.execute("MATCH (n)-[{no:2}]->(m) return m.hobbies as hobbies")
        hobbies = self.cur.fetchone()[0]
        self.assertEquals("reading", hobbies[0])
        self.cur.execute("MATCH (ee:person) WHERE ee.klout = 99 "
                         + "RETURN ee.name, to_jsonb(ee.name)")
        row = self.cur.fetchone()
        self.assertIsInstance(row[0], basestring) # if "str", error is occurred instead of "basestring"
        self.assertEquals("Emil", row[0])
        self.assertIsInstance(row[1], unicode)
        self.assertEquals('Emil', row[1])

class ReturnTest(BasicTest):
    def test_Return(self):
        self.cur.execute("RETURN 'be happy!', 1+1")
        row = self.cur.fetchone()
        self.assertEquals("be happy!", row[0])
        self.assertEquals(2, row[1])

class WhereTest(BasicTest):
    def setUp(self):
        BasicTest.setUp(self)
        self.cur.execute("CREATE VLABEL person")
        self.cur.execute("CREATE (:person { name: 'Emil', from: 'Sweden', klout: 99})")
    def test_Where(self):
        self.cur.execute("MATCH (ee:person) WHERE ee.name = 'Emil' RETURN ee")
        row = self.cur.fetchone()[0]
        self.assertEquals(99, row.props["klout"])
        self.cur.execute("MATCH (ee:person) WHERE ee.klout = 99 RETURN ee")
        self.cur.execute("MATCH (ee:person) WHERE ee.klout = %s RETURN ee", (99,))
        row = self.cur.fetchone()[0]
        self.assertEquals(99, row.props["klout"])
    def test_WhereBind(self):
        self.cur.execute("MATCH (ee:person) WHERE ee.from = %s RETURN ee", ('Sweden',))
        row = self.cur.fetchone()[0]
        self.assertEquals(99, row.props["klout"])
        self.cur.execute("MATCH (ee:person {'klout': %s}) RETURN ee.name", (99,))
        row = self.cur.fetchone()[0]
        self.assertIsInstance(row, basestring)
        self.assertEquals("Emil", row)
    def test_WhereBindJson(self):
        self.cur.execute("MATCH (ee:person) WHERE ee.name = %s RETURN ee", ("Emil",))
        row = self.cur.fetchone()[0]
        self.assertIsInstance(row, agtype.Vertex)
        self.assertEquals("Emil", row.props["name"])

if __name__ == '__main__':
    unittest.main()