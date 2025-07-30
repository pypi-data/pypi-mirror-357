import typing as t

from arguebuf.model import AbstractNode, NodeType

__all__ = ("dfs", "bfs", "node_distance")


# https://eddmann.com/posts/depth-first-search-and-breadth-first-search-in-python/
def dfs(
    start: NodeType,
    connections: t.Callable[[AbstractNode], t.AbstractSet[NodeType]],
    include_start: bool = True,
) -> list[NodeType]:
    # Need to use a dict since a set does not preserve order
    visited: dict[NodeType, None] = {}
    stack: list[NodeType] = [start]

    while stack:
        node = stack.pop()

        if node not in visited:
            visited[node] = None
            stack.extend(set(connections(node)) - visited.keys())

    if include_start:
        return list(visited.keys())

    return [node for node in visited if node != start]


def bfs(
    start: NodeType,
    connections: t.Callable[[AbstractNode], t.AbstractSet[NodeType]],
    include_start: bool = True,
) -> list[NodeType]:
    # Need to use a dict since a set does not preserve order
    visited: dict[NodeType, None] = {}
    queue: list[NodeType] = [start]

    while queue:
        node = queue.pop(0)

        if node not in visited:
            visited[node] = None
            queue.extend(set(connections(node)) - visited.keys())

    if include_start:
        return list(visited.keys())

    return [node for node in visited if node != start]


def node_distance(
    start_node: AbstractNode,
    end_node: AbstractNode,
    connections: t.Callable[[AbstractNode], t.Iterable[AbstractNode]],
    max_distance: int | None = None,
    directed: bool = True,
) -> int | None:
    """Get the distance between `start_node` and `end_node` in the graph.

    Args:
        start_node: Node object that is part of the graph.
        end_node: Node object that is part of the graph.
        connections: Callable containing links between nodes
            (e.g., `graph.incoming_atom_nodes` and `graph.outgoing_nodes`)
        max_distance: Only search for nodes having at most a distance of this argument.
            Especially helpful when dealing with large graphs where shorts paths are searched for.
        directed: If `False`, also search for the direction `end_node` -> `start_node`.

    Returns:
        Number of nodes in between or `None` if no path between

    Examples:
        >>> from arguebuf import Graph, AtomNode, SchemeNode, Edge
        >>> g = Graph()
        >>> n1 = AtomNode("Premise")
        >>> n2 = SchemeNode()
        >>> n3 = AtomNode("Claim")
        >>> e1 = Edge(n1, n2)
        >>> e2 = Edge(n2, n3)
        >>> g.add_node(n1)
        >>> g.add_node(n2)
        >>> len(g.nodes)
        2
        >>> g.add_edge(e1)
        >>> g.add_edge(e2)
        >>> len(g.edges)
        2
        >>> node_distance(n1, n3, g.outgoing_nodes)
        2
        >>> node_distance(n3, n1, g.outgoing_nodes)
    """

    if start_node == end_node:
        return 0

    dist = _directed_node_distance(start_node, end_node, connections, max_distance)

    if dist is None and not directed:
        dist = _directed_node_distance(end_node, start_node, connections, max_distance)

    return dist


def _directed_node_distance(
    start_node: AbstractNode,
    end_node: AbstractNode,
    connections: t.Callable[[AbstractNode], t.Iterable[AbstractNode]],
    max_distance: int | None = None,
) -> int | None:
    expansion: list[tuple[AbstractNode, int]] = [
        (n, 1) for n in connections(start_node)
    ]

    while len(expansion) > 0:
        candidate, distance = expansion.pop()

        if max_distance is not None and distance > max_distance:
            continue
        elif candidate == end_node:
            return distance
        else:
            expansion.extend((n, distance + 1) for n in connections(candidate))

    return None
