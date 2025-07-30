import pytest
from stream_buffer import StreamBuffer
from datetime import datetime, timedelta


def test_empty_buffer():
    buf = StreamBuffer(max_size=10)
    assert len(buf) == 0
    assert buf.get(0) is None
    assert buf.to_list() == []


def test_add_and_get():
    buf = StreamBuffer(max_size=5)
    for i in range(5):
        buf.add(f"data-{i}")
    assert len(buf) == 5
    for i in range(5):
        key, data = buf[i]
        assert data == f"data-{i}"
        assert key == float(i)
    # Test out of bounds
    with pytest.raises(IndexError):
        _ = buf[5]
    with pytest.raises(IndexError):
        _ = buf[-6]


def test_overwrite_when_full():
    buf = StreamBuffer(max_size=3)
    for i in range(5):
        buf.add(f"item-{i}")
    assert len(buf) == 3
    assert [d for _, d in buf] == ["item-2", "item-3", "item-4"]


def test_strictly_increasing_keys():
    buf = StreamBuffer(max_size=5)
    buf.add("a", key=1)
    buf.add("b", key=2)
    with pytest.raises(ValueError):
        buf.add("c", key=2)  # Not strictly increasing
    with pytest.raises(ValueError):
        buf.add("d", key=1.5)  # Not strictly increasing


def test_custom_keys():
    buf = StreamBuffer(max_size=3)
    buf.add("a", key=10)
    buf.add("b", key=20)
    buf.add("c", key=30)
    assert [k for k, _ in buf] == [10.0, 20.0, 30.0]


def test_datetime_keys():
    now = datetime.now()
    buf = StreamBuffer(max_size=2)
    buf.add("a", key=now)
    buf.add("b", key=now + timedelta(seconds=1))
    keys = [k for k, _ in buf]
    assert keys[1] > keys[0]


def test_get_force_exact():
    buf = StreamBuffer(max_size=5)
    for i in range(5):
        buf.add(f"d{i}", key=i * 2)
    assert buf.get(3, force_exact=True) is None
    assert buf.get(4, force_exact=False) == ("d1", "d2", "d3")
    assert buf.get(5, force_exact=False) == ("d2", None, "d3")
    assert buf.get(15, force_exact=False) == ("d4", None, None)
    assert buf.get(-1, force_exact=False) == (None, None, "d0")
    assert buf.get(2, force_exact=True) == "d1"


def test_get_range():
    buf = StreamBuffer(max_size=10)
    for i in range(10):
        buf.add(f"val-{i}", key=i)
    result = buf.get_range(3, 7)
    assert [d for _, d in result] == ["val-3", "val-4", "val-5", "val-6"]
    # Test range with no results
    assert buf.get_range(20, 30) == []
    # Test reversed range
    assert buf.get_range(7, 3) == []


def test_clear():
    buf = StreamBuffer(max_size=5)
    for i in range(5):
        buf.add(i)
    buf.clear()
    assert len(buf) == 0
    assert buf.to_list() == []


def test_init_with_data_and_keys():
    data = ["a", "b", "c", "d"]
    keys = [10, 20, 30, 40]
    buf = StreamBuffer(max_size=3, data=data, keys=keys)
    # Only last 3 should be present
    assert [d for _, d in buf] == ["b", "c", "d"]
    assert [k for k, _ in buf] == [20.0, 30.0, 40.0]


def test_init_with_data_only():
    data = ["x", "y", "z"]
    buf = StreamBuffer(max_size=5, data=data)
    assert [d for _, d in buf] == ["x", "y", "z"]
    assert [k for k, _ in buf] == [0.0, 1.0, 2.0]


def test_init_with_mismatched_keys_and_data():
    data = [1, 2]
    keys = [1]
    with pytest.raises(ValueError):
        StreamBuffer(max_size=5, data=data, keys=keys)


def test_init_with_keys_but_no_data():
    keys = [1, 2, 3]
    with pytest.raises(ValueError):
        StreamBuffer(max_size=5, keys=keys)


def test_getitem_indexing_and_slicing():
    buf = StreamBuffer(max_size=5)
    for i in range(5):
        buf.add(f"item-{i}", key=i)
    # Test positive indices
    for i in range(5):
        key, data = buf[i]
        assert key == float(i)
        assert data == f"item-{i}"
    # Test negative indices
    for i in range(1, 6):
        key, data = buf[-i]
        assert key == float(5 - i)
        assert data == f"item-{5 - i}"
    # Test out of bounds
    with pytest.raises(IndexError):
        _ = buf[5]
    with pytest.raises(IndexError):
        _ = buf[-6]
    # Test slicing
    slice_result = buf[1:4]
    assert slice_result == [buf[1], buf[2], buf[3]]
    # Test full slice
    assert buf[:] == [buf[i] for i in range(5)]
    # Test step in slice
    assert buf[::2] == [buf[0], buf[2], buf[4]]


def test_iter():
    buf = StreamBuffer(max_size=3)
    items = ["a", "b", "c"]
    for i, val in enumerate(items):
        buf.add(val, key=i)
    # __iter__ should yield (key, data) tuples in order
    iterated = list(buf)
    assert iterated == [(0.0, "a"), (1.0, "b"), (2.0, "c")]
    # After overwrite
    buf.add("d", key=3)
    iterated = list(buf)
    assert iterated == [(1.0, "b"), (2.0, "c"), (3.0, "d")]


def test_contains():
    buf = StreamBuffer(max_size=4)
    for i in range(4):
        buf.add(f"val-{i}", key=i*10)
    # Existing keys
    assert 0 in buf
    assert 10 in buf
    assert 30 in buf
    # Non-existing keys
    assert 5 not in buf
    assert 25 not in buf
    # After overwrite
    buf.add("val-4", key=40)
    assert 0 not in buf
    assert 10 in buf
    assert 40 in buf


def test_stress_mixed_operations():
    buf = StreamBuffer(max_size=5)
    # Add initial items
    for i in range(3):
        buf.add(f"init-{i}", key=i)
    assert len(buf) == 3
    # Check contains
    assert 0 in buf and 2 in buf and 3 not in buf
    # Add more to fill and overwrite
    for i in range(3, 8):
        buf.add(f"val-{i}", key=i)
    # Now buffer should have keys 3,4,5,6,7
    assert [k for k, _ in buf] == [3.0, 4.0, 5.0, 6.0, 7.0]
    # Test get for present and missing keys
    assert buf.get(5) == "val-5"
    assert buf.get(2) is None
    # Test get with neighbors
    assert buf.get(4.5, force_exact=False) == ("val-4", None, "val-5")
    # Test get_range
    range_items = buf.get_range(4, 7)
    assert [d for _, d in range_items] == ["val-4", "val-5", "val-6"]
    # Test slicing
    assert buf[1:4] == [buf[1], buf[2], buf[3]]
    # Test negative indexing
    assert buf[-1] == (7.0, "val-7")
    # Test iteration
    iterated = list(buf)
    assert iterated == [(3.0, "val-3"), (4.0, "val-4"), (5.0, "val-5"), (6.0, "val-6"), (7.0, "val-7")]
    # Clear and reuse
    buf.clear()
    assert len(buf) == 0
    buf.add("after-clear", key=100)
    assert buf.get(100) == "after-clear"
    with pytest.raises(IndexError):
        buf[222]
    assert list(buf) == [(100.0, "after-clear")] 