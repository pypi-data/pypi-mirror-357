import typing as t


class Node(t.TypedDict):
    id: str
    title: str  # title of argument/statement
    type: str  # check if "argument-map-node", or "statement-map-node"
    labelTitle: str  # title of argument/statement
    labelText: str  # text of argument/statement


class Edge(t.TypedDict):
    id: str
    type: str
    relationType: str
    source: str
    target: str


class Map(t.TypedDict):
    nodes: list[Node]
    edges: list[Edge]


class Graph(t.TypedDict):
    map: Map
