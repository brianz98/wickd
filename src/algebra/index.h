#pragma once

#include <cstdint>
#include <string>
#include <vector>

#include "helpers/hash_utils.hpp"
#include "wickd-def.h"

/**
 * @brief A class to represent orbital indices.
 *
 * This class represents an orbital index that appears in a second quantized
 * expression.  It holds the space type (via an index to the corresponding
 * space defined in the OrbitalSpaceInfo object) and the numerical label of
 * index.
 *
 * For example, if OrbitalSpaceInfo defines an occupied space ("o"),
 * the index o_1 corresponds to:
 *
 *     "o_1" -> Index(0,1)
 *
 */
class Index {
public:
  // ==> Constructors <==
  Index();

  Index(int space, int p);

  // ==> Class public interface <==

  /// @return the orbital space type
  int space() const { return index_.first; }

  /// @return the position within a space
  int pos() const { return index_.second; }

  /// Comparison operator
  /// @return true if other index is equal to this
  bool operator==(Index const &other) const;

  /// Less than operator (used for sorting)
  /// @return true if other index is greater to this
  bool operator<(Index const &other) const;

  /// @return a string representation
  /// (e.g., for index 1 of space 'o' returns 'o1')
  std::string str() const;

  /// @return a LaTeX representation
  /// This function either returns a pretty index (e.g., 'i')
  /// or a generic index (e.g., 'o1')
  std::string latex() const;

  /// @return a compilable representation (e.g., 'o1')
  std::string compile(const std::string &format) const;

private:
  // ==> Class private data <==

  /// Store the orbital space type and position in the space (space,p)
  std::pair<int, int> index_;
};

// Hash specialization for Index (pair<int,int>)
template <> struct ankerl::unordered_dense::hash<Index> {
  using is_avalanching = void; // skip internal mixing step
  // pack [space, pos] into a 64-bit integer and hash it
  uint64_t operator()(Index const &idx) const noexcept {
    // Encode space and pos as a 64-bit integer and hash it via wyhash.
    std::uint64_t v =
        (static_cast<std::uint64_t>(idx.space()) << 32) |
        static_cast<std::uint64_t>(static_cast<uint32_t>(idx.pos()));
    return hash_utils::hash_first(v);
  }
};

// A Index -> Index map used for reindexing (flat open-addressed hash map)
using index_map_t = ankerl::unordered_dense::map<Index, Index>;

// Helper functions

/// Helper function to make an Index object from a space label and position
/// Accepts inputs of the form "o0", "o_0"
Index make_index_from_str(const std::string &index);
std::vector<Index> make_indices_from_str(const std::string &index);

/// Print to an output stream
std::ostream &operator<<(std::ostream &os, const Index &idx);

// Special functions

/// Canonicalize a set of indices
scalar_t canonicalize_indices(std::vector<Index> &indices, bool reversed);

/// A function that takes two lists of indices and creates a index map for the
/// second list that voids duplicates
index_map_t remap(const std::vector<Index> &idx_vec1,
                  const std::vector<Index> &idx_vec2);

/// Helper function that counts the number of spaces in a vector of indices
std::vector<int> num_indices_per_space(const std::vector<Index> &indices);

/// Return the symmetry factor of a product of indices
/// This is the product n1! x n2! x n3! x ... where ni is the number of
/// indices that belong to orbital space i
int symmetry_factor(const std::vector<Index> &indices);
