"""Modular negation, `|x> -> |(-x) mod p>`.

Extracted from ``notebooks/mod_neg.ipynb``.
"""
from math import log2

from qiskit import QuantumCircuit, QuantumRegister

from implementations.utils.helpers import complement
from implementations.arithmetic_operations.Haner.adder_class import haner_class_adder


def mod_negation(n: int, p: int) -> QuantumCircuit:
    """Negates a register modulo :attr:`p`, in place.

    Uses `-x mod p = p - x` for `x <= p`, and the identity `p - x = ~(~p + x)`, where
    `~a` is the bitwise complement over `n` bits. That turns the subtraction into a
    classical-constant addition followed by a complement, so no comparison and no
    ancilla are needed.

    The circuit has the following effect, given `0 < x < p`:

    |x, anc> -> |(p - x), anc>

    .. note::
        `x = 0` is **not** a fixed point: it maps to `|p>` instead of `|0>`. Callers
        that may feed the additive identity have to special-case it.

        :attr:`n` must equal `p.bit_length()`; the complement mask is derived from `p`,
        so a wider register silently produces a wrong result.

    Register order:
        `x` (n) | `anc` (1)

    Args:
        n (int): number of qubits of the operand, `n = p.bit_length()`.
        p (int): the modulus.

    Returns:
        quantum_circuit(QuantumCircuit): the circuit implementing the operation.

    Reference:
    -
        Quantum resource estimates for computing elliptic curve discrete logarithms.
        Martin Roetteler, Michael Naehrig, Krysta M. Svore, Kristin Lauter. arXiv:1706.06752
    """
    reg_x = QuantumRegister(n, name="x")
    reg_anc = QuantumRegister(1, name="anc")

    quantum_circuit = QuantumCircuit(reg_x, reg_anc, name="mod_neg")

    p_compl = p ^ (2**(int(log2(p)) + 1) - 1)

    quantum_circuit.append(haner_class_adder(p_compl, n).to_gate(), reg_x[:] + reg_anc[:])
    quantum_circuit.compose(complement(n), reg_x[:], inplace=True)

    return quantum_circuit
