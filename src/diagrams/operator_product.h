#pragma once

#include "helpers/product.hpp"
#include "operator.h"
#include "wickd-def.h"

class OperatorProduct : public Product<Operator> {
public:
  /// Constructors
  OperatorProduct() : Product<Operator>() {}
  OperatorProduct(Product<Operator> &&opprod) : Product<Operator>(opprod) {}
  OperatorProduct(const std::vector<Operator> &operators)
      : Product<Operator>(operators) {}
  OperatorProduct(std::initializer_list<Operator> operators)
      : Product<Operator>(operators) {}

  scalar_t canonicalize();

  int num_ops() const;
};

OperatorProduct operator*(const OperatorProduct &l, const OperatorProduct &r);

/// Hash function for OperatorProduct
template <> struct ankerl::unordered_dense::hash<OperatorProduct> {
  uint64_t operator()(OperatorProduct const &op) const noexcept {
    uint64_t h = 0;
    hash_utils::hash_range(h, op);
    return h;
  }
};
