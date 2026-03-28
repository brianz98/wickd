#pragma once

#include <string>
#include <vector>

#include "helpers/hash_utils.hpp"
#include "index.h"
#include "wickd-def.h"

/// Enums
enum class SymmetryType { Symmetric, Antisymmetric, Nonsymmetric };

/// This class represents a tensor labeled with orbital indices.
/// It holds information about the label and the indices of the tensor.
class Tensor {

public:
  // ==> Constructors <==
  explicit Tensor() {}

  Tensor(const std::string &label, const std::vector<Index> &lower,
         const std::vector<Index> &upper, SymmetryType symmetry);

  // ==> Class public interface <==

  /// Return a reference to the label
  const std::string &label() const { return label_; }

  /// Return a reference to the lower indices
  const std::vector<Index> &lower() const { return lower_; }

  /// Return a reference to the upper indices
  const std::vector<Index> &upper() const { return upper_; }

  /// Is this tensor complex conjugated?
  bool is_complex_conjugate() const { return is_complex_conjugate_; }

  /// Return a reference to the symmetry
  SymmetryType symmetry() const { return symmetry_; }

  /// Set the lower indices
  void set_lower(const std::vector<Index> &indices) { lower_ = indices; }

  /// Set the upper indices
  void set_upper(const std::vector<Index> &indices) { upper_ = indices; }

  /// Set the complex conjugate flag
  void set_complex_conjugate(bool val) { is_complex_conjugate_ = val; }

  /// Return a vector containing all indices
  std::vector<Index> indices() const;

  /// Reindex this tensor
  void reindex(index_map_t &idx_map);

  /// Canonicalize this tensor and return the overall phase factor
  scalar_t canonicalize();

  /// Return the adjoint of this tensor
  Tensor adjoint() const;

  /// Return the rank of the tensor
  std::int64_t rank() const {
    return static_cast<std::int64_t>(lower_.size() + upper_.size());
  }

  /// return the signature (number of upper/lower indices in each space)
  std::vector<std::pair<int, int>> signature() const;

  /// Return the symmetry factor of this tensor
  int symmetry_factor() const;

  /// Comparison operator used for sorting
  bool operator<(Tensor const &other) const;

  /// Comparison operator used for sorting
  bool operator==(Tensor const &other) const;

  /// Return a string representation
  std::string str() const;

  /// Return a LaTeX representation
  std::string latex() const;

  /// Return a compilable representation
  std::string compile(const std::string &format) const;

private:
  // ==> Class private data <==

  std::string label_;        // label of the tensor
  std::vector<Index> lower_; // lower indices
  std::vector<Index> upper_; // upper indices
  SymmetryType symmetry_; // symmetry of the tensor (symmetric, antisymmetric,
                          // or nonsymmetric)
  bool is_complex_conjugate_ = false; // is this tensor complex conjugated?
};

/// A function to construct a tensor
Tensor make_tensor(const std::string &label,
                   const std::vector<std::string> &lower,
                   const std::vector<std::string> &upper,
                   SymmetryType symmetry);

/// Helper function to make a Tensor object from a string
/// Accepts inputs of the form "t_{o0}^{v_0}"
Tensor make_tensor_from_str(const std::string &index, SymmetryType symmetry);

/// Print to an output stream
std::ostream &operator<<(std::ostream &os, const Tensor &tensor);

/// Hash function for Tensor
template <> struct ankerl::unordered_dense::hash<Tensor> {
  uint64_t operator()(Tensor const &t) const noexcept {
    uint64_t h = ankerl::unordered_dense::hash<std::string>{}(t.label());
    hash_utils::hash_range(h, t.lower());
    hash_utils::hash_range(h, t.upper());
    hash_utils::hash_combine(h, static_cast<int>(t.symmetry()));
    hash_utils::hash_combine(h, t.is_complex_conjugate());
    return h;
  }
};
