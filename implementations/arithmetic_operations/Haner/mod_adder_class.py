"""Modular classical-constant adder of Häner, Roetteler and Svore.

Extracted from ``notebooks/mod_adder_class.ipynb``.
"""
from qiskit import QuantumCircuit, QuantumRegister

from implementations.utils.helpers import complement
from implementations.arithmetic_operations.Haner.adder_class import (
    carry_with_const,
    haner_class_adder,
)


def comparator_class(c: int, n: int) -> QuantumCircuit:
    """Compares an n-qubit register with a classical constant :attr:`c`.

    Toggles the `carry` qubit when `x < c`. It is :func:`carry_with_const` applied to
    the complement of `x`: the carry-out of `~x + c` is set exactly when `x < c`.

    The circuit has the following effect:

    |x, g, carry> -> |x, g, carry ⊕ [x < c]>

    Register order:
        `a` (n) | `g` (n-1) | `carry` (1)

    Args:
        c (int): the classical constant to compare against, at most `n` bits.
        n (int): number of qubits of the quantum operand.

    Returns:
        quantum_circuit(QuantumCircuit): the circuit implementing the operation.

    Reference:
    -
        Factoring using 2n+2 qubits with Toffoli based modular multiplication.
        Thomas Häner, Martin Roetteler, Krysta M. Svore. arXiv:1611.07995
    """
    reg_a = QuantumRegister(n, name="a")
    reg_g = QuantumRegister(n - 1, name="g")
    reg_carry = QuantumRegister(1, name="carry")
    quantum_circuit = QuantumCircuit(reg_a, reg_g, reg_carry, name="comparator_class")

    quantum_circuit.compose(complement(n), reg_a[:], inplace=True)
    quantum_circuit.compose(carry_with_const(c, n), reg_a[:] + reg_g[:] + reg_carry[:], inplace=True)
    quantum_circuit.compose(complement(n), reg_a[:], inplace=True)

    return quantum_circuit


def haner_mod_class_adder(c: int, n: int, p: int) -> QuantumCircuit:
    """Adds a classical constant :attr:`c` to an n-qubit register modulo :attr:`p`.

    The circuit has the following effect, given the promise `0 <= x < p` and `0 <= c < p`:

    |x, g, anc> -> |(x + c) mod p, g, anc>

    It works by comparing `x` against `p - c`:

    - if `x < p - c` there is no wrap-around, so `anc` is set and `c` is added;
    - otherwise the result is `x - (p - c)`, obtained by subtracting `p - c`.

    The final comparison against `c` restores `anc` to `|0>` (the trailing `x` gate
    accounts for the inverted polarity).

    The `g` register holds `n-1` *dirty* qubits borrowed by the comparator and is
    returned to its original state; the inner adders take `g[0]` as their own dirty
    ancilla, which is why they are built with `dirty=True`.

    Register order:
        `x` (n) | `g` (n-1) | `anc` (1)

    Args:
        c (int): the classical constant, `0 <= c < p`.
        n (int): number of qubits of the quantum operand, `n = p.bit_length()`.
        p (int): the modulus.

    Returns:
        quantum_circuit(QuantumCircuit): the circuit implementing the operation.

    Reference:
    -
        Factoring using 2n+2 qubits with Toffoli based modular multiplication.
        Thomas Häner, Martin Roetteler, Krysta M. Svore. arXiv:1611.07995
    """
    reg_x = QuantumRegister(n, name="x")
    reg_g = QuantumRegister(n - 1, name="g")
    reg_anc = QuantumRegister(1, name="anc")

    quantum_circuit = QuantumCircuit(reg_x, reg_g, reg_anc, name="mod_class_adder")

    quantum_circuit.append(comparator_class(p - c, n).to_gate(), reg_x[:] + reg_g[:] + reg_anc[:])

    quantum_circuit.append(haner_class_adder(c, n, dirty=True).to_gate().control(1), reg_anc[:] + reg_x[:] + reg_g[0:1])
    quantum_circuit.append(haner_class_adder(p - c, n, dirty=True).to_gate().inverse().control(1, ctrl_state="0"), reg_anc[:] + reg_x[:] + reg_g[0:1])

    quantum_circuit.append(comparator_class(c, n).to_gate(), reg_x[:] + reg_g[:] + reg_anc[:])
    quantum_circuit.x(reg_anc)

    return quantum_circuit
