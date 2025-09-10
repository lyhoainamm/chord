# chord_on.py
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import random

def in_interval_open_closed(x: int, a: int, b: int, M: int) -> bool:
    # (a, b] theo vòng modulo M
    if a < b:
        return a < x <= b
    return x > a or x <= b

class Node:
    def __init__(self, node_id: int, ring: "Ring"):
        self.id = node_id
        self.ring = ring
        self.successor: "Node" = self
        self.predecessor: Optional["Node"] = None
        self.store: Dict[int, str] = {}

    def find_successor(self, key: int, count_hops: bool = False) -> Tuple["Node", int] | "Node":
        """Tuyến tính qua danh sách node đã sort: O(N)."""
        hops = 0
        arr = self.ring.nodes()
        if not arr:
            return (self, 0) if count_hops else self
        for n in arr:
            hops += 1
            if n.id >= key:
                return (n, hops) if count_hops else n
        return (arr[0], hops + 1) if count_hops else arr[0]  # wrap-around

    def put(self, key: int, val: str) -> None:
        owner = self.find_successor(key)
        if isinstance(owner, tuple): owner = owner[0]
        owner.store[key] = val

    def get(self, key: int):
        owner = self.find_successor(key)
        if isinstance(owner, tuple): owner = owner[0]
        return owner.store.get(key)

class Ring:
    def __init__(self, m: int):
        self.m = m
        self.M = 1 << m
        self._nodes: Dict[int, Node] = {}

    def nodes(self) -> List[Node]:
        return sorted(self._nodes.values(), key=lambda n: n.id)

    def _relink_all(self) -> None:
        arr = self.nodes()
        n = len(arr)
        if n == 0: return
        for i, node in enumerate(arr):
            node.predecessor = arr[(i - 1) % n]
            node.successor   = arr[(i + 1) % n]

    def add_node(self, node_id: int) -> Node:
        assert 0 <= node_id < self.M
        if node_id in self._nodes: return self._nodes[node_id]
        node = Node(node_id, self)
        self._nodes[node_id] = node
        self._relink_all()
        # chuyển dữ liệu (pred(node), node] từ successor về node
        succ = node.successor
        if succ is not None:
            to_move = []
            for k in list(succ.store.keys()):
                if in_interval_open_closed(k, node.predecessor.id, node.id, self.M):
                    to_move.append(k)
            for k in to_move:
                node.store[k] = succ.store.pop(k)
        return node

    def remove_node(self, node_id: int) -> None:
        node = self._nodes.pop(node_id, None)
        if not node: return
        if node.successor and node.successor is not node:
            node.successor.store.update(node.store)  # không mất dữ liệu
        node.store.clear()
        self._relink_all()

    @classmethod
    def from_ids(cls, m: int, ids: List[int]) -> "Ring":
        r = cls(m)
        for nid in sorted(set(ids)):
            r.add_node(nid)
        return r

    # tiện tạo dữ liệu ngẫu nhiên
    def put_many_random(self, nkeys: int, seed: int = 0) -> None:
        random.seed(seed)
        if not self._nodes: return
        src = self.nodes()[0]
        for _ in range(nkeys):
            k = random.randrange(0, self.M)
            src.put(k, f"v{k}")
