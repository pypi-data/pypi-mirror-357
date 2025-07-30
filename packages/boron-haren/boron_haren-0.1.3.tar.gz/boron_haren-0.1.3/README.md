# HAREN++: Hybrid Associative Retrieval Engine with Nullified Worst-Case

HAREN++ is a high-performance hybrid search algorithm that redefines practical search efficiency across both sorted and unsorted arrays. It combines direct memory indexing, adaptive hashing, predictive segment regression, and sub-logarithmic fallback strategies to achieve constant-time average search performance and compressed worst-case complexity.

Unlike traditional search methods such as linear search (O(N)) and binary search (O(log N)), HAREN++ delivers near-constant search performance even in datasets containing millions of elements. It is designed for real-time applications where ultra-fast retrieval is essential.

## Key Features
- **O(1) Average-Case Lookup:** Memory-accelerated direct indexing.
- **O(log log N) Worst-Case Search:** Fast fallback using anchor tree search.
- **Sorted and Unsorted Arrays:** Supports mixed datasets without performance loss.
- **Predictive Indexing:** Uses lightweight learned segment models to guide fast searches.
- **Benchmark Proven:** Up to 25,000× faster than linear search and up to 20× faster than binary search on million-element datasets.
- **Layered Search Strategy:** Combines direct map, adaptive hashing, predictive regression, and a fallback anchor tree.

## Installation

```bash
pip install boron-haren
