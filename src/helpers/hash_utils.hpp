#pragma once

#include "helpers/unordered_dense.h"

/// Utilities for building ankerl::unordered_dense hash specializations.
///
/// Two building blocks:
///   hash_combine(seed, v)      — hash v and mix it into seed
///   hash_range(seed, range)    — hash_combine every element of a range
///
/// Typical usage:
///   auto h = hash_utils::hash_first(obj.first_field());
///   hash_utils::hash_combine(h, obj.second_field());
///   hash_utils::hash_range(h, obj.collection());
///   return h;

namespace hash_utils {

/// Hash a single value — use this to seed h for the first field.
template <typename T>
inline uint64_t hash_first(const T &v) {
  return ankerl::unordered_dense::hash<T>{}(v);
}

/// Mix a pre-computed 64-bit hash value into the running seed.
/// Uses the boost::hash_combine mixing step.
inline void hash_combine(uint64_t &h, uint64_t v) {
  h ^= v + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2);
}

/// Hash value v using ankerl::unordered_dense::hash<T> and mix into seed.
template <typename T>
inline void hash_combine(uint64_t &h, const T &v) {
  hash_combine(h, ankerl::unordered_dense::hash<T>{}(v));
}

/// Hash every element of range and mix each into seed.
template <typename Range>
inline void hash_range(uint64_t &h, const Range &r) {
  for (const auto &v : r) {
    hash_combine(h, v);
  }
}

} // namespace hash_utils
