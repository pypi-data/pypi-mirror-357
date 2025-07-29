from typing import TypeVar, Generic, cast, TextIO, Protocol
from collections import deque, OrderedDict

T = TypeVar("T")


class Writable(Protocol):
    def write(self, s: str, /) -> int:
        ...


class StrFile(Writable):
    def __init__(self) -> None:
        self.chunks = []

    def write(self, s: str, /) -> int:
        self.chunks.append(s)
        return len(s)

    def to_str(self) -> str:
        from functools import reduce

        # keep initial value in case list is empty
        return reduce(str.__add__, self.chunks, "")

    def to_file(self, f: Writable) -> None:
        f.write(self.to_str())


class Node:
    class NodeSupport:
        def __init__(self, visited: bool = False, linked_by: "Node | None" = None):
            self.visited = visited
            self.linked_by = linked_by

        def reset(self):
            self.visited = False
            self.linked_by = None

    def __repr__(self):
        return f"Node(data={repr(self.data)}, connections={len(self.connections)}, visited={self.support.visited})"

    def __init__(self, obj: object):
        self.data = obj
        self.connections = OrderedDict()
        self.support = Node.NodeSupport()

    def __hash__(self) -> int:
        return hash((self.data))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented

        return other.data == self.data and other.connections == other.connections

    def connect(self, other: "Node"):
        self.connections[other] = True

    def disconnect(self, other: "Node"):
        del self.connections[other]

    def is_connected(self, other: "Node") -> bool:
        return other in self.connections

    def bfs(self, value: object) -> deque["Node"]:
        result = deque()
        q = deque()
        q.append(self)
        q.extend(self.connections)

        while q:
            this: Node | None = cast(Node, q.popleft())
            if this.support.visited:
                continue
            if this.data == value:
                while this is not None:
                    result.appendleft(this)
                    this = this.support.linked_by
                break
            else:
                this.support.visited = True
                for neighbor in this.connections:
                    if not neighbor.support.visited:
                        neighbor.support.linked_by = this
                        q.append(neighbor)

        return result

    def dfs(self, value: object) -> deque["Node"]:
        def impl(this: "Node", result: deque[Node]):
            if this.support.visited:
                return False

            if this.data == value:
                walker: Node | None = this
                while walker:
                    result.appendleft(walker)
                    walker = walker.support.linked_by
                return True

            this.support.visited = True
            for item in this.connections:
                if not item.support.visited:
                    item.support.linked_by = this
                    if impl(item, result):
                        break

        r = deque()
        impl(self, r)
        return r

    def reset(self):
        self.support.reset()


import re

line_sep = re.compile(r"\r?\n")
con_sep = re.compile(r",\s*")
comment = re.compile(r"\s*#.*?\n")


class Graph(Generic[T]):
    @classmethod
    def fromgraphstr(cls: type["Graph[str]"], s: str) -> "Graph[str]":
        s = comment.sub("", s)
        lines = line_sep.split(s)
        if lines[0][0] == "!":
            directive = lines.pop(0)
            if directive == "!nodir":
                directed = False
            elif directive == "!dir":
                directed = True
            else:
                directed = False
        else:
            directed = False

        g = cls(directed=directed)
        to_connect = []
        for line in (i for i in lines if i):
            line = line.strip()
            i = line.index(":")
            if line[0] == "!":
                raise ValueError("Cannot have !directive that is not the first line")
            if line[i] == line[-1]:
                # node with no connections; bail
                g.add(line[:i])
            else:
                name, connections = line[:i].strip(), line[i + 1 :].strip()
                g.add(name)
                if len(connections) > 0:
                    for con in con_sep.split(connections):
                        # cannot connect nodes until all nodes are added
                        to_connect.append((name, con))

        # once all nodes are added do the connections
        for start, end in to_connect:
            g.connect(start, end)

        return g

    def __init__(
        self, *values: T, connections: dict[T, T] | None = None, directed: bool = True
    ):
        self.nodes: dict[T, Node] = {}
        self.directed = directed

        for value in values:
            self.add(value)

        if connections:
            for start, end in connections.items():
                self.connect(start, end)

    def __getitem__(self, v: T) -> Node:
        return self.checked_get(v)

    def __str__(self):
        return ", ".join(
            f"Graph[{i}[{len(i.connections)} conns.]]" for i in self.nodes.values()
        )

    def reset(self):
        for node in self.nodes.values():
            node.reset()

    def add(self, value: T):
        self.nodes[value] = Node(value)

    def has(self, value: T) -> bool:
        return value in self.nodes

    def dfs(self, start: T, value: T) -> list[T]:
        if start not in self.nodes:
            raise ValueError("No such starting node") from None

        r = [cast(T, i.data) for i in self.nodes[start].dfs(value)]
        self.reset()
        return r

    def bfs(self, start: T, value: T) -> list[T]:
        if start not in self.nodes:
            raise ValueError("No such starting node") from None

        r = [cast(T, i.data) for i in self.nodes[start].bfs(value)]
        self.reset()
        return r

    def checked_get(self, v: T) -> Node:
        if not self.has(v):
            raise ValueError("No such value {!r} in graph".format(v))
        return self.nodes[v]

    def disconnect(self, v1: T, v2: T) -> bool:
        n1 = self[v1]
        n2 = self[v2]

        if not n1.is_connected(n2):
            return False

        n1.disconnect(n2)
        if not self.directed:
            n2.disconnect(n1)
        return True

    def connect(self, value1: T, value2: T) -> bool:
        n1 = self[value1]
        n2 = self[value2]

        if n1.is_connected(n2) and self.directed:
            return False

        if (n1.is_connected(n2) and n2.is_connected(n1)) and not self.directed:
            return False

        n1.connect(n2)
        if not self.directed:
            n2.connect(n1)
        return True

    def is_connected(self, value1: T, value2: T) -> bool:
        # reciprocal check not needed since connect() will connect in both directions if not directed
        return self[value1].is_connected(self[value2])

    def tographstring(self, f: Writable, *, simple: bool = False):
        if simple and self.directed:
            import warnings

            warnings.warn("`simple` parameter is meaningless for directed graphs")

        if self.directed:
            f.write("!dir\n")
        else:
            f.write("!nodir\n")

        if simple and not self.directed:
            seen = set()
            for node in self.nodes:
                f.write(f"{node}: ")
                for idx, val in enumerate(self.nodes[node].connections):
                    if (val.data, node) in seen:
                        continue
                    if idx == len(self.nodes[node].connections) - 1:
                        f.write(f"{val.data}")
                    else:
                        f.write(f"{val.data}, ")

                    seen.add((node, val.data))
                f.write("\n")
        else:
            for node in self.nodes:
                f.write(f"{node}: ")
                f.write(f'{", ".join(i.data for i in self.nodes[node].connections)}')
                f.write("\n")


if __name__ == "__main__":
    # example
    # print("This is an example usage of the Graph data structure")
    # print("You probably want to use an import instead")
    # print("See: test/friends.gsf and pytomutil/graph.py")
    # with open("test/friends.gsf") as f:
    #     g = Graph.fromgraphstr(f.read())

    # print(g)
    # print(g.bfs("alice", "dave"))
    with open("test/complex.gsf") as f:
        g = Graph.fromgraphstr(f.read())

    print(g.dfs("a", "j"))
    print(g.bfs("a", "j"))

    with open("test/output.gsf", "w") as h:
        g.tographstring(h, simple=True)
