#include <algorithm>
#include <nanobind/make_iterator.h>
#include <nanobind/nanobind.h>
#include <nanobind/stl/map.h>
#include <nanobind/stl/pair.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/string_view.h>
#include <nanobind/stl/vector.h>

#include "algebra/expression.h"

namespace nb = nanobind;
using namespace nanobind::literals;

/// Export the Indexclass
void export_Expression(nb::module_ &m) {
  nb::class_<Expression>(m, "Expression")
      .def(nb::init<>())
      .def("__repr__", &Expression::str)
      .def("__str__", &Expression::str)
      .def("__len__", &Expression::size)
      .def("__eq__", &Expression::operator==)
      .def("__neg__", [](const Expression &rhs) { return -rhs; })
      .def("__add__",
           [](Expression lhs, const Expression &rhs) {
             lhs += rhs;
             return lhs;
           })
      .def("__sub__",
           [](Expression rhs, const Expression &lhs) {
             rhs -= lhs;
             return rhs;
           })
      .def("__matmul__",
           [](Expression rhs, const Expression &lhs) {
             rhs *= lhs;
             return rhs;
           })
      .def("__mul__",
           [](Expression rhs, scalar_t r) {
             rhs *= r;
             return rhs;
           })       
      .def(
          "__iadd__",
          [](Expression &lhs, const Term &term) -> Expression & {
            lhs += {term.symterm(), term.coefficient()};
            return lhs;
          },
          nb::is_operator()) // Bind in-place addition with Term
      .def(
          "__iadd__",
          [](Expression &lhs,
             const std::pair<SymbolicTerm, scalar_t> &term) -> Expression & {
            lhs += term;
            return lhs;
          },
          nb::is_operator()) // Bind in-place addition with Term
      .def(
          "__iadd__",
          [](Expression &lhs, const SymbolicTerm &sterm) -> Expression & {
            lhs += {sterm, scalar_t(1)};
            return lhs;
          },
          nb::is_operator()) // Bind in-place addition with Term
      .def(
          "__iter__",
          [](const Expression &e) -> nb::object {
            std::vector<std::pair<SymbolicTerm, scalar_t>> sorted(e.begin(),
                                                                   e.end());
            std::sort(sorted.begin(), sorted.end(),
                      [](const auto &a, const auto &b) {
                        return a.first < b.first;
                      });
            nb::list lst;
            for (const auto &p : sorted) {
              lst.append(nb::cast(p));
            }
            return lst.attr("__iter__")();
          })
      .def("dot", &Expression::dot, "rhs"_a)
      .def("norm", &Expression::norm)
      .def("latex", &Expression::latex, "sep"_a = " \\\\ \n")
      .def("to_manybody_equation", &Expression::to_manybody_equation)
      .def("to_manybody_equations", &Expression::to_manybody_equation)
      .def("canonicalize", &Expression::canonicalize)
      .def("adjoint", &Expression::adjoint,
           "Return the adjoint of this expression")
      .def("vacuum_normal_ordered", &Expression::vacuum_normal_ordered,
           "only_same_index_contractions"_a = false,
           "Return a vacuum normal ordered version of this expression")
      //  .def("normal_ordered", &Expression::normal_ordered,
      //       "only_same_index_contractions"_a = false,
      //       "Return a vacuum normal ordered version of this expression")
      .def("is_vacuum_normal_ordered", &Expression::is_vacuum_normal_ordered,
           "Return true if this expression is vacuum normal ordered")
      .def("add_from_string", &Expression::add_from_string,
           "Add a term to the expression from a string")
      .def(
      "add_from_strings",
           [](Expression& self, const std::vector<std::string_view>& vec_strings) -> Expression& {
              for (const auto& s : vec_strings) self.add_from_string(s);
              return self;
           },  nb::rv_policy::reference);

  m.def("operator_expr", &make_operator_expr, "label"_a, "components"_a,
        "normal_ordered"_a, "symmetry"_a = SymmetryType::Antisymmetric,
        "coefficient"_a = scalar_t(1));

  m.def("expression", &make_expression, "s"_a,
        "symmetry"_a = SymmetryType::Antisymmetric);
}
