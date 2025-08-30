""" Hash Table ADT

Defines a Hash Table using a modified Linear Probe implementation for conflict resolution.
"""
from __future__ import annotations
__author__ = 'Jackson Goerner'
__since__ = '07/02/2023'

from data_structures.referential_array import ArrayR
from typing import TypeVar, Generic

K = TypeVar('K')
V = TypeVar('V')


class FullError(Exception):
    pass


class HashyStepTable(Generic[K, V]):
    """
    Hashy Step Table.

    Type Arguments:
        - K:    Key Type. In most cases should be string.
                Otherwise `hash` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    # No test case should exceed 1 million entries.
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241, 786433, 1572869]

    HASH_BASE = 31

    SENTINEL_DELETED = object()

    def __init__(self, sizes=None) -> None: # Done
        """
        Initialise the Hash Table.

        Complexity:
        Best Case Complexity: O(M | N) where M is the first table size in self.TABLE_SIZES (if sizes is None)
                              and N is the first table size in sizes.
        Worst Case Complexity: O(M | N) where M is the first table size in self.TABLE_SIZES (if sizes is None)
                               and N is the first table size in sizes.
        """
        if sizes is not None:
            self.TABLE_SIZES = sizes
        self.size_index = 0
        self.array: ArrayR[tuple[K, V] | None] = ArrayR(self.TABLE_SIZES[self.size_index])
        self.count = 0

    def hash(self, key: K) -> int:
        """
        Hash a key for insert/retrieve/update into the hashtable.

        Complexity:
        Best Case Complexity: O(len(key))
        Worst Case Complexity: O(len(key))
        """

        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % self.table_size
            a = a * self.HASH_BASE % (self.table_size - 1)
        return value

    def hash2(self, key: K) -> int:
        """
        Used to determine the step size for our hash table.

        Complexity:
        Best Case Complexity: O(N) where N is the length of the key.
        Worst Case Complexity: O(N) where N is the length of the key.
        """
        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % (self.table_size - 1) 
            a = a * self.HASH_BASE % (self.table_size - 1) # Make sure that probing to the same position is impossible, otherwise infinite loop.
        return value + 1 # Make sure it does not return 0
    
    @property
    def table_size(self) -> int:
        return len(self.array)

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        """
        return self.count

    def _hashy_probe(self, key: K, is_insert: bool) -> int: # Done
        """
        Find the correct position for this key in the hash table using hashy probing.

        Raises:
        KeyError: When the key is not in the table, but is_insert is False.
        FullError: When a table is full and cannot be inserted.

        Complexity:
        Best Case Complexity: O(N) where N is the length of the key to be hashed. This occurs when the key is hashed 
                              to an unoccupied position and is_insert is True or to the correct position for retrieval 
                              and is_insert is False. Since no collision occurs, no further probing is needed.

        Worst Case Complexity: O(M + N) where M is the length of the key to be hashed and N is the self.table_size. This 
                               occurs when the key is hashed to the wrong position occupied by a different key (when is_insert 
                               is false) or to an occupied position (when is_insert is true) causing collision and probing is done 
                               many times to find the suitable position depending on the context. In the worst case, the table is 
                               searched all the way through, contributing to O(N).
        """
        position = self.hash(key)
        step = None
        first_empty_index = None

        while True:
            if self.is_full():
                break        

            elif self.array[position] is None or self.array[position] == HashyStepTable.SENTINEL_DELETED:
                if is_insert:
                    return position
                elif self.array[position] == HashyStepTable.SENTINEL_DELETED:
                    if not first_empty_index:
                        first_empty_index = position
                    if not step:
                        step = self.hash2(key)
                    position = (position + step) % self.table_size
                else:
                    raise KeyError(key)
                
            elif self.array[position][0] == key:
                if first_empty_index:
                    self.array[first_empty_index], self.array[position] = self.array[position], self.array[first_empty_index]
                    position = first_empty_index
                return position
            else:
                if not step:
                    step = self.hash2(key)
                position = (position + step) % self.table_size

        if is_insert:
            raise FullError("Table is full!")
        else:
            raise KeyError(key)
    
    def keys(self) -> list[K]:
        """
        Returns all keys in the hash table.

        :complexity: O(N) where N is self.table_size.
        """
        res = []
        for x in range(self.table_size):
            if self.array[x] is not None and self.array[x] != HashyStepTable.SENTINEL_DELETED: 
                res.append(self.array[x][0])
        return res

    def values(self) -> list[V]:
        """
        Returns all values in the hash table.

        :complexity: O(N) where N is self.table_size.
        """
        res = []
        for x in range(self.table_size):
            if self.array[x] is not None and self.array[x] != HashyStepTable.SENTINEL_DELETED: 
                res.append(self.array[x][1])
        return res

    def __contains__(self, key: K) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See hashy probe.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, key: K) -> V:
        """
        Get the value at a certain key

        :complexity: See hashy probe.
        :raises KeyError: when the key doesn't exist.
        """
        position = self._hashy_probe(key, False)
        return self.array[position][1]

    def __setitem__(self, key: K, data: V) -> None:
        """
        Set an (key, value) pair in our hash table.

        :complexity: See hashy probe.
        :raises FullError: when the table cannot be resized further.
        """

        position = self._hashy_probe(key, True)

        if self.array[position] is None and self.array[position] != HashyStepTable.SENTINEL_DELETED: 
            self.count += 1

        self.array[position] = (key, data)

        if len(self) > self.table_size * 2 / 3:
            self._rehash()

    def __delitem__(self, key: K) -> None:
        """
        Deletes a (key, value) using lazy deletion

        Complexity:
        Best Case Complexity: O(_hashy_probe) where best case of _hashy_probe is applied.
        Worst Case Complexity: O(_hashy_probe) where worst of _hashy_probe is applied.
        """
        position = self._hashy_probe(key, False)
        self.array[position] = HashyStepTable.SENTINEL_DELETED
        self.count -= 1

    def is_empty(self) -> bool:
        return self.count == 0

    def is_full(self) -> bool:
        return self.count == self.table_size

    def _rehash(self) -> None: # Done
        """
        Need to resize table and reinsert all values

        Complexity:
        Best Case Complexity: O(K * L) where K is self.table_size before resizing and L is the length of the longest key 
                              to be hashed. This occurs when the keys are always hashed to an unoccupied position in the new 
                              table, so no further probing is needed because there are no collisions. This assumes the new table
                              size used is approximately the same as the previous table size just slightly larger, for the best case.
                              O(K) is due to traversing the entire old table to locate the keys and values to be transferred to the 
                              larger new table.

        Worst Case Complexity: O(K * (L + M)) where K is the self.table_size before resizing, L is the length of the longest key top be
                               hashed and M is the new self.table_size. This occurs when the keys are hashed to occupied positions in the 
                               new table causing collisions and probing is done many times using hashy probe to find an unoccupied position. 
                               In the worst case, the new table is searched all the way through, contributing to O(M). O(K * (L + M)) > Complexity 
                               of initializing the new table with the new table size, so it is not included.  O(K) is due to traversing the entire
                               old table to locate the keys and values to be transferred to the larger new table.
        """
        old_array = self.array
        self.size_index += 1
        if self.size_index == len(self.TABLE_SIZES):
            return
        self.array = ArrayR(self.TABLE_SIZES[self.size_index])
        self.count = 0
        for item in old_array: 
            if item is not None and item != HashyStepTable.SENTINEL_DELETED:
                key, value = item
                self[key] = value 


    def __str__(self) -> str:
        """
        Returns all they key/value pairs in our hash table (no particular
        order).
        :complexity: O(N * (str(key) + str(value))) where N is the table size
        """
        result = ""
        for item in self.array:
            if item is not None:
                (key, value) = item
                result += "(" + str(key) + "," + str(value) + ")\n"
        return result
    
