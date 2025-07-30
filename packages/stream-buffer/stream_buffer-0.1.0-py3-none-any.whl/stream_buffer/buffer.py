from typing import Optional, List, Union, Any, Tuple
from datetime import datetime
import numpy as np
import threading


class StreamBuffer:
    """
    A high-performance, thread-safe circular buffer for stream data with strictly increasing keys.

    Supports O(1) appending and O(log n) retrieval by key using binary search.
    Suitable for time-series, ticker, or sequential data in streaming applications.
    """
    def __init__(
        self,
        max_size: int = 100000,
        keys: Optional[List[Union[str, float, int, datetime]]] = None,
        data: Optional[List[Any]] = None,
    ):
        """
        Initialize the StreamBuffer.

        Args:
            max_size (int): Maximum number of items the buffer can hold.
            keys (Optional[List[Union[str, float, int, datetime]]]): Optional list of keys (must be strictly increasing if provided with data).
            data (Optional[List[Any]]): Optional list of data to initialize the buffer. If more than max_size, only the most recent items are kept.

        Raises:
            ValueError: If keys and data are both provided but their lengths do not match, or if keys are provided without data.
        """
        self.max_size = max_size
        self._keys = np.zeros(max_size, dtype=np.float64)
        self._data = np.empty(max_size, dtype=object)
        self._start_idx = 0
        self._end_idx = 0
        self.size = 0
        self._lock = threading.RLock()

        if data is not None:
            start_pos = max(0, len(data) - self.max_size)
            sliced_data = data[start_pos:]

            if keys is None:
                keys = list(range(start_pos, len(data)))
            else:
                if len(keys) != len(data):
                    raise ValueError("Length of 'keys' and 'data' must match.")
                keys = keys[start_pos:]

            for key, val in zip(keys, sliced_data):
                self.add(val, key)

        elif keys is not None:
            raise ValueError("'data' must be provided when 'keys' is given.")

    def __getitem__(self, idx):
        """
        Get item(s) by index or slice.

        Args:
            idx (int or slice): Index or slice to retrieve.

        Returns:
            Tuple[float, Any] or List[Tuple[float, Any]]: (key, data) tuple or list of such tuples.

        Raises:
            IndexError: If index is out of bounds.
            TypeError: If idx is not int or slice.
        """
        with self._lock:
            if isinstance(idx, slice):
                start, stop, step = idx.indices(self.size)
                return [
                    self[i]  # recursively call __getitem__ for each index
                    for i in range(start, stop, step)
                ]
            elif isinstance(idx, int):
                if not -self.size <= idx < self.size:
                    raise IndexError("Index out of bounds")
                if idx < 0:
                    idx += self.size
                real_idx = self._logical_to_physical(idx)
                return self._keys[real_idx], self._data[real_idx]
            else:
                raise TypeError(f"Invalid argument type: {type(idx).__name__}")

    def __iter__(self):
        """
        Iterate over all (key, data) pairs in the buffer in order.

        Yields:
            Tuple[float, Any]: (key, data) tuples.
        """
        with self._lock:
            for i in range(self.size):
                real_idx = self._logical_to_physical(i)
                yield self._keys[real_idx], self._data[real_idx]

    def __contains__(self, key):
        """
        Check if a key exists in the buffer.

        Args:
            key (Union[str, float, int, datetime]): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        with self._lock:
            _, exact, _ = self._binary_search_with_neighbors(self._parse_key(key))
            return exact is not None

    def __len__(self) -> int:
        """
        Get the number of items currently in the buffer.

        Returns:
            int: Number of items in the buffer.
        """
        with self._lock:
            return self.size

    def add(self, data: Any, key: Optional[Union[str, float, int, datetime]] = None):
        """
        Append a new item to the buffer.

        Args:
            data (Any): The data to add.
            key (Optional[Union[str, float, int, datetime]]): The key for the data. If None, auto-increments from the last key.

        Raises:
            ValueError: If the key is not strictly greater than the last key.
        """
        with self._lock:
            if self.size == 0:
                last_key = -1
            else:
                last_key_pos = self._logical_to_physical(self.size - 1)
                last_key = self._keys[last_key_pos]

            new_key = self._parse_key(key) if key is not None else last_key + 1

            if new_key <= last_key:
                raise ValueError("Keys must be strictly increasing.")

            if self.size == self.max_size:
                self._start_idx = (self._start_idx + 1) % self.max_size
            else:
                self.size += 1

            self._keys[self._end_idx] = new_key
            self._data[self._end_idx] = data
            self._end_idx = (self._end_idx + 1) % self.max_size

    def get(
        self, key: Union[str, float, int, datetime], force_exact: bool = True
    ) -> Union[Any, Tuple[Any, Any], None]:
        """
        Retrieve data by key.

        Args:
            key (Union[str, float, int, datetime]): The key to search for.
            force_exact (bool): If True, only return data for an exact key match. If False, return neighbors as well.

        Returns:
            Any: Data for the exact key if found and force_exact is True, else None.
            Tuple[Any, Any, Any]: (lower_data, exact_data, higher_data) if force_exact is False.
        """
        with self._lock:
            if self.size == 0:
                return None

            target_key = self._parse_key(key)
            lower_logical, exact_logical, higher_logical = (
                self._binary_search_with_neighbors(target_key)
            )

            if force_exact:
                if exact_logical is not None:
                    real_idx = self._logical_to_physical(exact_logical)
                    return self._data[real_idx]
                return None
            else:
                exact_data = None
                lower_data = None
                higher_data = None

                if exact_logical is not None:
                    real_idx = self._logical_to_physical(exact_logical)
                    exact_data = self._data[real_idx]

                if lower_logical is not None:
                    lower_real_idx = self._logical_to_physical(lower_logical)
                    lower_data = self._data[lower_real_idx]

                if higher_logical is not None:
                    higher_real_idx = self._logical_to_physical(higher_logical)
                    higher_data = self._data[higher_real_idx]

                return (lower_data, exact_data, higher_data)

    def get_range(
        self,
        start_key: Union[str, float, int, datetime],
        end_key: Union[str, float, int, datetime],
    ) -> List[Tuple[float, Any]]:
        """
        Retrieve a range of items by key.

        Args:
            start_key (Union[str, float, int, datetime]): Start of the key range (inclusive).
            end_key (Union[str, float, int, datetime]): End of the key range (exclusive).

        Returns:
            List[Tuple[float, Any]]: List of (key, data) tuples in the specified range.
        """
        with self._lock:
            if self.size == 0:
                return []

            start_key = self._parse_key(start_key)
            end_key = self._parse_key(end_key)

            if start_key > end_key:
                return []

            lower_logical, exact_logical, higher_logical = (
                self._binary_search_with_neighbors(start_key)
            )

            if exact_logical is not None:
                start_idx = exact_logical
            elif higher_logical is not None:
                start_idx = higher_logical
            else:
                return []

            result = []
            logical_idx = start_idx

            while logical_idx < self.size:
                real_idx = self._logical_to_physical(logical_idx)
                key_at_pos = self._keys[real_idx]

                if key_at_pos >= end_key:
                    break

                result.append((key_at_pos, self._data[real_idx]))
                logical_idx += 1

            return result

    def to_list(self) -> List[Tuple[float, Any]]:
        """
        Convert the buffer to a list of (key, data) tuples.

        Returns:
            List[Tuple[float, Any]]: All items in the buffer in order.
        """
        with self._lock:
            return [
                (
                    self._keys[self._logical_to_physical(i)],
                    self._data[self._logical_to_physical(i)],
                )
                for i in range(self.size)
            ]

    def clear(self):
        """
        Remove all items from the buffer.
        """
        with self._lock:
            self._start_idx = 0
            self._end_idx = 0
            self.size = 0

    def _binary_search_with_neighbors(
        self, target_key: float
    ) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """
        Binary search for a key and its neighbors (private).

        Args:
            target_key (float): The key to search for.

        Returns:
            Tuple[Optional[int], Optional[int], Optional[int]]: (lower_idx, exact_idx, higher_idx)
        """
        if self.size == 0:
            return (None, None, None)

        left, right = 0, self.size - 1
        exact_idx = None
        lower_idx = None
        higher_idx = None

        while left <= right:
            mid = (left + right) // 2
            mid_idx = self._logical_to_physical(mid)
            mid_key = self._keys[mid_idx]

            if mid_key == target_key:
                exact_idx = mid
                if mid > 0:
                    lower_idx = mid - 1
                if mid < self.size - 1:
                    higher_idx = mid + 1
                break
            elif mid_key < target_key:
                lower_idx = mid
                left = mid + 1
            else:
                higher_idx = mid
                right = mid - 1

        return (lower_idx, exact_idx, higher_idx)

    def _parse_key(self, key: Union[str, float, int, datetime]) -> float:
        """
        Convert a key to a float (private).

        Args:
            key (Union[str, float, int, datetime]): The key to convert.

        Returns:
            float: The key as a float.
        """
        if isinstance(key, datetime):
            return key.timestamp()
        return float(key)

    def _logical_to_physical(self, logical_idx: int) -> int:
        """
        Convert a logical index to a physical index in the circular buffer (private).

        Args:
            logical_idx (int): Logical index.

        Returns:
            int: Physical index in the underlying arrays.
        """
        return (self._start_idx + logical_idx) % self.max_size
