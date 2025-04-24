```
  ,-.       _,---._ __  / \
 /  )    .-'       `./ /   \
(  (   ,'            `/    /|
 \  `-"             \'\   / |
  `.              ,  \ \ /  |
   /`.          ,'-`----Y   |
  (            ;        |   '
  |  ,-.    ,-'         |  /
  |  | (   |        hjw | /
  )  |  \  `.___________|/
  `--'   `--'
```

While Neo4j is fun, it's pricing isnt. But fortunately Open Souce is and hence this repo is used to setup a local Janus Graph DB, populate it with company data that can optionally be augmented by syntetically generated data


# How to use Janus Graph DB 


## Setup (Dockerized) 

Starting out be fetching and running the latest janusgraph container 

```
$ docker run -it -p 8182:8182 janusgraph/janusgraph
```

I noticed some issues when scanning the container using `grypher`. Those issues can be found in the `vulnerabilites.txt` for further assessment. 


## Communication with the DB

You can simply start another container, that sets up a gramlin console as a client via: 

```
docker run --rm --link janusgraph-default:janusgraph -e GREMLIN_REMOTE_HOSTS=janusgraph \
    -it janusgraph/janusgraph:latest ./bin/gremlin.sh
```

In case you're extra curious, you can play around with it, using the [Tinkerpop Tutorial](https://tinkerpop.apache.org/docs/3.7.3/tutorials/getting-started/).

Alternatively you can also use UI Tools like 
- G.V()


## Populate Janus with RDF
For this purpose, I found many suitable approaches. Due to the project requirements, I sticked to a simple Bulk-Load. 

#### Bulk Loading
    - Preprocessing RDF Data: Convert RDF data (e.g., Turtle or RDF/JSON) into a format compatible with JanusGraph, such as CSV or JSON.

    - Enable Batch Loading: Set storage.batch-loading=true in the configuration file to optimize bulk loading performance.

    - Parallelization: Use Hadoop-Gremlin or other parallelization techniques to load large datasets efficiently.

    - Load Vertices and Edges Separately: First load vertex data, followed by edge data, ensuring consistency between IDs.



The simplest way to load a given raw file into JanusGraph is the following Groovy Script: 

```Groovy
graph = TinkerGraph.open()
graph.createIndex('userId', Vertex.class) //1

g = traversal().withEmbedded(graph)

getOrCreate = { id ->
  g.V().has('user','userId', id).
    fold().
    coalesce(unfold(),
             addV('user').property('userId', id)).next()  //2
}

new File('wiki-Vote.txt').eachLine {
  if (!it.startsWith("#")){
    (fromVertex, toVertex) = it.split('\t').collect(getOrCreate) //3
    g.addE('votesFor').from(fromVertex).to(toVertex).iterate()
  }
}

```


Alternatively, one could also work directly with Python: 


```python
v1 = g.addV('person').property('name','marko').next()
v2 = g.addV('person').property('name','stephen').next()
g.V(v1).addE('knows').to(v2).property('weight',0.75).iterate()
```

or 

```python
import csv

with open('data.csv') as file:
    reader = csv.DictReader(file)
    for row in reader:
        g.addV(row['label']).property('name', row['name']).property('age', int(row['age'])).next()
```

### Indexing
By default  Graph indices are automatically chosen by JanusGraph to answer which ask for all vertices $(g.V)$ or all edges $(g.E)$ that satisfy one or multiple constraints (e.g. has or interval).


## Python and Janus


Python and Janus work together like a charm. 
Just install gremlinpython: 

`pip install gremlinpython`

Using the following setup 

```
from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal

connection = DriverRemoteConnection('ws://localhost:8182/gremlin', 'g')
g = traversal().withRemote(connection)

```
### Insertion
```
v1 = g.addV('person').property('name','marko').next()
v2 = g.addV('person').property('name','stephen').next()
g.V(v1).addE('knows').to(v2).property('weight',0.75).iterate()
```

### Traversal

```
hercules_age = g.V().has('name', 'hercules').values('age').next()
print(f'Hercules is {hercules_age} years old.')
```



## Cool Open Source Visualistion Solutions for Janus
### Python Libraries
- [NetworkX](https://networkx.org/)
- [PyVis](https://pyvis.readthedocs.io/en/latest/#)
### General Solutions
- [GraphExp](https://github.com/bricaud/graphexp)
- [Jaal](https://github.com/imohitmayank/jaal)

## Troubleshooting 



