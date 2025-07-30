# harenpp/haren.py
import bisect
import numpy as np
from collections import defaultdict
from math import log2

class HAREN:
    def __init__(self, arr, num_segments=None):
        self.arr = arr
        self.n = len(arr)
        self.sorted = self._is_sorted()

        self.index_map = {}
        self.hash_buckets = defaultdict(list)
        self.segment_models = []
        self.segment_bounds = []
        self.anchor_tree = []

        self.num_segments = num_segments or max(1, int(log2(self.n or 2)))
        self.segment_size = max(1, self.n // self.num_segments)

        self.min_val = min(arr) if arr else 0
        self.max_val = max(arr) if arr else 0

        self._initialize()

    def _is_sorted(self):
        return all(self.arr[i] <= self.arr[i + 1] for i in range(self.n - 1)) if self.n > 1 else True

    def _initialize(self):
        if self.n == 0:
            return

        for i, val in enumerate(self.arr):
            if val not in self.index_map:
                self.index_map[val] = i
            self.hash_buckets[val % self.num_segments].append((val, i))

        for s in range(self.num_segments):
            start = s * self.segment_size
            end = min((s + 1) * self.segment_size, self.n)
            block = self.arr[start:end]

            self.segment_bounds.append((start, end))

            if len(block) <= 1 or len(set(block)) <= 1:
                self.segment_models.append((0, 0))
                self.anchor_tree.append((block[0] if block else None, start))
                continue

            x = np.array(block)
            y = np.arange(len(block))

            try:
                a, b = np.polyfit(x, y, 1)
            except Exception:
                a, b = 0, 0

            self.segment_models.append((a, b))
            self.anchor_tree.append((block[len(block)//2], start))

        self.anchor_tree.sort()

    def _fallback_anchor_tree_search(self, target):
        lo, hi = 0, len(self.anchor_tree) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            val, idx = self.anchor_tree[mid]
            if val == target:
                return idx
            elif val < target:
                lo = mid + 1
            else:
                hi = mid - 1

        if lo < len(self.anchor_tree):
            start = self.anchor_tree[lo][1]
        else:
            start = self.anchor_tree[-1][1]

        end = min(start + self.segment_size, self.n)
        block = self.arr[start:end]
        idx = bisect.bisect_left(block, target)
        if idx < len(block) and block[idx] == target:
            return start + idx
        return -1

    def search(self, target):
        if target in self.index_map:
            return self.index_map[target]

        bucket_key = target % self.num_segments
        for val, idx in self.hash_buckets[bucket_key]:
            if val == target:
                return idx

        if self.sorted and self.max_val > self.min_val:
            segment_idx = int((target - self.min_val) / (self.max_val - self.min_val + 1e-9) * self.num_segments)
            segment_idx = max(0, min(self.num_segments - 1, segment_idx))

            start, end = self.segment_bounds[segment_idx]
            block = self.arr[start:end]

            if len(block):
                idx_in_block = bisect.bisect_left(block, target)
                if idx_in_block < len(block) and block[idx_in_block] == target:
                    return start + idx_in_block

        return self._fallback_anchor_tree_search(target)
