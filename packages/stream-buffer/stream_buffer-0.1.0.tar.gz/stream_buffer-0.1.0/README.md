# stream-buffer 

A lightweight circular buffer for handling stream data with fast appending and retrieval.

## Motivation

While working with live ticker data from okx, I realized that there was no lightweight buffer that offers fast appending and range based queries for streaming applications. Thus this buffer was created to address this gap.


## Use Cases

- You need fast time-based appends and efficient range retrievals.

- You want to store only the latest N entries (rolling buffer).

- You’re working with streaming APIs, market data, sensor feeds, or event logs.

- You need custom indexing (e.g., timestamps, floats) but want lower overhead than Pandas.

- You want a minimal and dependency-light alternative to DataFrames or reactive pipelines.


## Installation

```bash
pip install stream-buffer
```


## Example

```python
from stream_buffer import StreamBuffer
from datetime import datetime, timedelta

# Initialize a buffer with a maximum size of 3
timestamps = [datetime.now() + timedelta(seconds=i) for i in range(5)]
buf = StreamBuffer(max_size=3)

# Add items with explicit datetime keys
for i, ts in enumerate(timestamps):
    buf.add(f"price-{i}", key=ts)

# The buffer now contains only the last 3 items (circular behavior)
print("Buffer contents (key, value):")
for k, v in buf:
    print(k, v)

# Access by index (supports negative indices)
print("\nFirst item:", buf[0])
print("Last item:", buf[-1])

# Slicing
print("\nSlice [0:2]:", buf[0:2])

# Membership test (by key)
key_to_check = buf[1][0]
print(f"\nIs key {key_to_check} in buffer?", key_to_check in buf)

# Get by key (exact and neighbors)
print("\nGet by exact key:", buf.get(key_to_check))
print("Get by non-existent key (neighbors):", buf.get(key_to_check + 0.5, force_exact=False))

# Range query (all items between two keys)
start_key = buf[0][0]
end_key = buf[-1][0]
print("\nRange query:", buf.get_range(start_key, end_key))

# Convert to list
print("\nBuffer as list:", buf.to_list())

# Buffer length
print("\nBuffer length:", len(buf))

# Clear the buffer
buf.clear()
print("\nBuffer cleared. Length:", len(buf))
```

**Expected Output**
```
Buffer contents (key, value):
1750881382.592505 price-2
1750881383.592508 price-3
1750881384.59251 price-4

First item: (np.float64(1750881382.592505), 'price-2')
Last item: (np.float64(1750881384.59251), 'price-4')

Slice [0:2]: [(np.float64(1750881382.592505), 'price-2'), (np.float64(1750881383.592508), 'price-3')]

Is key 1750881383.592508 in buffer? True

Get by exact key: price-3
Get by non-existent key (neighbors): ('price-3', None, 'price-4')

Range query: [(np.float64(1750881382.592505), 'price-2'), (np.float64(1750881383.592508), 'price-3')]

Buffer as list: [(np.float64(1750881382.592505), 'price-2'), (np.float64(1750881383.592508), 'price-3'), (np.float64(1750881384.59251), 'price-4')]

Buffer length: 3

Buffer cleared. Length: 0
```


