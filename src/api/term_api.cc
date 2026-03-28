#include <nanobind/nanobind.h>
#include <nanobind/stl/pair.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>

#include "algebra/term.h"

namespace nb = nanobind;
using namespace nanobind::literals;

/// Export the Indexclass
void export_SymbolicTerm(nb::module_ &m) {
  nb::class_<SymbolicTerm>(m, "SymbolicTerm")

      .def(nb::init<>())
      .def("__repr__", &SymbolicTerm::str)
      .def("__str__", &SymbolicTerm::str)
      .def("latex", &SymbolicTerm::latex)
      .def("add", nb::overload_cast<const std::vector<SQOperator> &>(
                      &SymbolicTerm::add))
      .def("add", nb::overload_cast<const SQOperator &>(&SymbolicTerm::add))
      .def("add", nb::overload_cast<const Tensor &>(&SymbolicTerm::add))
      .def("set", nb::overload_cast<const std::vector<SQOperator> &>(
                      &SymbolicTerm::set))
      .def("normal_ordered", &SymbolicTerm::normal_ordered)
      .def("set_normal_ordered", &SymbolicTerm::set_normal_ordered)
      .def("ops", &SymbolicTerm::ops)
      .def("tensors", &SymbolicTerm::tensors)
      .def("__eq__",
           [](const SymbolicTerm &l, const SymbolicTerm &r) { return l == r; })
      .def("__lt__",
           [](const SymbolicTerm &l, const SymbolicTerm &r) { return l < r; })
      .def("nops", &SymbolicTerm::nops)
      .def("adjoint", &SymbolicTerm::adjoint)
      .def("is_vacuum_normal_ordered", &SymbolicTerm::is_vacuum_normal_ordered)
      .def("is_labeled_normal_ordered",
           &SymbolicTerm::is_labeled_normal_ordered)
      .def("is_creation_then_annihilation",
           &SymbolicTerm::is_creation_then_annihilation)
      .def("compile", &SymbolicTerm::compile)
      .def("vacuum_normal_order", &SymbolicTerm::vacuum_normal_order,
           "only_same_index_contractions"_a = false);

  nb::class_<Term>(m, "Term")
      .def(nb::init<>())
      .def(nb::init<const SymbolicTerm>())
      .def("__repr__", &Term::str)
      .def("__str__", &Term::str)
      .def("latex", &Term::latex)
      .def("add",
           nb::overload_cast<const std::vector<SQOperator> &>(&Term::add))
      .def("add", nb::overload_cast<const SQOperator &>(&Term::add))
      .def("add", nb::overload_cast<const Tensor &>(&Term::add))
      .def("set", nb::overload_cast<scalar_t>(&Term::set))
      .def("set_normal_ordered", &Term::set_normal_ordered)
      .def("coefficient", &Term::coefficient)
      .def("symterm", &Term::symterm);
}