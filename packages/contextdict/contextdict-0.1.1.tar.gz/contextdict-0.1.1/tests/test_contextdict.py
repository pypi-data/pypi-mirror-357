import time
import pytest
from contextdict import ContextDict

def test_basic_set_get():
    hd = ContextDict()
    hd.set("a", 1)
    assert hd.get("a") == 1

def test_ttl_expiry():
    hd = ContextDict()
    hd.set("temp", "val", ttl=1)
    time.sleep(1.1)
    assert hd.get("temp") is None

def test_versioning():
    hd = ContextDict()
    hd.set("vkey", 1)
    t1 = time.time()
    time.sleep(0.5)
    hd.set("vkey", 2)
    t2 = time.time()  # ⬅️ Move this BEFORE setting version 3
    time.sleep(0.5)
    hd.set("vkey", 3)

    assert hd.get("vkey", version=t1) == 1
    assert hd.get("vkey", version=t2) == 2

def test_filter():
    hd = ContextDict()
    hd.set("a", 1)
    hd.set("b", 2)
    result = hd.filter(lambda k, v: v % 2 == 0)
    assert result == {"b": 2}

def test_dict_syntax():
    hd = ContextDict()
    hd["x"] = 99
    assert hd["x"] == 99
    del hd["x"]
    assert "x" not in hd
