# AgensGraph Python driver

It is AgensGraph client for Python, supports the graph data types like Vertex, Edge and Path used in AgensGraph.

It is based on [psycopg2](https://github.com/psycopg/psycopg2).


## Install

```sh
$ pip install -U pip
$ pip install psycopg2

$ python /path/to/set.py install

```


## Example

```python
import psycopg2

connect = psycopg2.connect("dbname=agens user=bylee host=127.0.0.1")
cur = connect.cursor()
cur.execute("DROP GRAPH IF EXISTS g CASCADE")
cur.execute("CREATE GRAPH g")
cur.execute("SET graph_path = g")

cur.execute("CREATE p=(:v{name: 'agens'})-[:e]->() RETURN p")
cur.execute("MATCH ()-[r]->() RETURN count(*)")
print cur.fetchone()[0]

```



## Test

```sh
$ python test_agtype [-v]

```

The test cases must be executed in Python 2.x
