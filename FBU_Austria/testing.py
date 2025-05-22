from typing import Optional
def add_edge(g: GraphTraversalSource, from_id: int, to_id: int, edge_label: str, param: Optional[str] = None):
   g.V(from_id).addE(edge_label).to(__.V(to_id)).property("param", param).next()
def add_vertex(g: GraphTraversalSource, vertex_label: str, vertex_id: int, name: Optional[str] = None):
   g.addV(vertex_label).property(T.id, vertex_id).property("name", name).next()
def init_toy_graph(g: GraphTraversalSource):
   g.V().drop().iterate()  # so you can run this cell more than ones
   g.E().drop().iterate()  # so you can run this cell more than ones
   add_vertex(g, "user", 1, name="Olivia")
   add_vertex(g, "user", 2, name="Emma")
   add_vertex(g, "file", 3, name="your_new_idea.pdf")
   add_vertex(g, "file", 4, name="salary.pdf")
   add_vertex(g, "file", 5, name="demo.py")
   add_vertex(g, "file", 6, name="blog.html")
   add_vertex(g, "drive", 7, name="my_drive")
   add_edge(g, 1, 2, "edit")
   add_edge(g, 1, 3, "edit")
   add_edge(g, 1, 4, "view")
   add_edge(g, 2, 5, "print")
   add_edge(g, 2, 6, "edit")
   add_edge(g, 3, 7, "located_in")
init_toy_graph(g)
# count how many
print(g.V().valueMap(True).toList())  # get a list of all of the vertices
"""
[{<T.id: 1>: 1, <T.label: 4>: 'user', 'name': ['Olivia']}, {<T.id: 1>: 2, <T.label: 4>: 'user', 'name': ['Emma']}, {<T.id: 1>: 3, <T.label: 4>: 'file', 'name': ['your_new_idea.pdf']}, {<T.id: 1>: 4, <T.label: 4>: 'file', 'name': ['salary.pdf']}, {<T.id: 1>: 5, <T.label: 4>: 'file', 'name': ['demo.py']}, {<T.id: 1>: 6, <T.label: 4>: 'file', 'name': ['blog.html']}, {<T.id: 1>: 7, <T.label: 4>: 'drive', 'name': ['my_drive']}]
"""
print(g.E().valueMap(True).toList())  # get a list of all of the edges
"""
[{<T.id: 1>: 1024, <T.label: 4>: 'view'}, {<T.id: 1>: 1025, <T.label: 4>: 'print'}, {<T.id: 1>: 1026, <T.label: 4>: 'edit'}, {<T.id: 1>: 1027, <T.label: 4>: 'located_in'}, {<T.id: 1>: 1022, <T.label: 4>: 'edit'}, {<T.id: 1>: 1023, <T.label: 4>: 'edit'}]
"""