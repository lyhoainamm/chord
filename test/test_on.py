# test_on.py
import math
from chord_on import Ring

def test_put_get_basic():
    r = Ring.from_ids(m=6, ids=[1,5,9,12,20,33,47,60])
    # 3->5, 18->20, 62 wrap->1
    r.nodes()[0].put(3,"A")
    r.nodes()[0].put(18,"B")
    r.nodes()[0].put(62,"C")
    assert r.nodes()[3].get(3)  == "A"
    assert r.nodes()[4].get(18) == "B"
    assert r.nodes()[2].get(62) == "C"
    assert r.nodes()[1].get(17) is None

def test_links_ring_invariant():
    r = Ring.from_ids(m=6, ids=[1,5,9,12,20,33,47,60])
    arr = r.nodes()
    assert [n.id for n in arr] == [1,5,9,12,20,33,47,60]
    for i, n in enumerate(arr):
        assert n.successor is arr[(i+1)%len(arr)]
        assert n.predecessor is arr[(i-1)%len(arr)]

def test_join_moves_boundary_keys():
    r = Ring.from_ids(m=6, ids=[10,30,50])
    for k in [2,9,10,11,19,20,21,29,30,31,49,50,63]:
        r.nodes()[0].put(k, f"v{k}")
    before = sum(len(n.store) for n in r.nodes())
    r.add_node(20)  # nhận keys trong (10,20]
    node20 = [n for n in r.nodes() if n.id==20][0]
    assert "v11" in node20.store.values()
    assert "v19" in node20.store.values()
    after = sum(len(n.store) for n in r.nodes())
    assert after == before  # không mất dữ liệu

def test_leave_keeps_data_and_links():
    r = Ring.from_ids(m=6, ids=[1,5,9,12,20,33,47,60])
    r.put_many_random(600, seed=7)
    total_before = sum(len(n.store) for n in r.nodes())
    r.remove_node(20)
    total_after = sum(len(n.store) for n in r.nodes())
    assert total_after == total_before
    ids = [n.id for n in r.nodes()]
    assert 20 not in ids
    arr = r.nodes()
    for i, n in enumerate(arr):
        assert n.successor is arr[(i+1)%len(arr)]
        assert n.predecessor is arr[(i-1)%len(arr)]

def test_lookup_hops_linear_bound():
    r = Ring.from_ids(m=6, ids=[1,5,9,12,20,33,47,60])
    for key in [0,1,4,5,6,18,21,59,60,62]:
        owner, hops = r.nodes()[0].find_successor(key, count_hops=True)
        assert owner.id in [1,5,9,12,20,33,47,60]
        assert 1 <= hops <= len(r.nodes()) + 1  # O(N) bound
