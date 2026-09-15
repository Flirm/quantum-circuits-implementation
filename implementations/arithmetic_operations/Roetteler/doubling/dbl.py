"""Modular doubling, `|x> -> |2x mod N>`.

Extracted from ``notebooks/dbl.ipynb``.
"""
from math import log2

from qiskit import QuantumCircuit, QuantumRegister

from implementations.arithmetic_operations.Haner.adder_class import haner_class_adder


def mult_by_2(n: int) -> QuantumCircuit:
    """Multiplies an n-qubit register by 2 through a chain of swaps.

    Acts on `n+1` qubits: the extra top qubit receives the overflow bit, so the
    operation is exact rather than modulo `2^n`.

    |x, 0> -> |2x> (over n+1 qubits)

    Args:
        n (int): number of qubits of the operand (the circuit has `n+1` qubits).

    Returns:
        quantum_circuit(QuantumCircuit): the circuit implementing the operation.
    """
    quantum_circuit = QuantumCircuit(n+1, name="mult_by_2")

    for i in range(n-1, -1, -1):
        quantum_circuit.swap(i, i+1)
    return quantum_circuit


def double_mod(N: int) -> QuantumCircuit:
    """Doubles a register modulo :attr:`N`, in place.

    Given the promise `0 <= x < N`, `N` odd, and `anc` at `|00>`:

    |x, 00> -> |2x mod N, 00>

    The shift puts the exact value `2x` in `(anc[0], x)`; subtracting `N` from that
    `n+1`-bit value leaves `anc[0]` set iff `2x < N`, which drives the conditional
    add-back. Because `N` is odd, `2x mod N` is even exactly when no reduction
    happened, so `x[0]` alone suffices to uncompute `anc[0]`.

    Register order:
        `x` (n) | `anc` (2), with `n = int(log2(N)) + 1`

    Args:
        N (int): the modulus, must be odd.

    Returns:
        quantum_circuit(QuantumCircuit): the circuit implementing the operation.

    Reference:
    -
        Quantum resource estimates for computing elliptic curve discrete logarithms.
        Martin Roetteler, Michael Naehrig, Krysta M. Svore, Kristin Lauter. arXiv:1706.06752
    """
    n = int(log2(N)) + 1
    reg_x = QuantumRegister(n, name="x")
    reg_anc = QuantumRegister(2, name="anc")
    quantum_circuit = QuantumCircuit(reg_x, reg_anc, name="double_mod")

    quantum_circuit.append(mult_by_2(n).to_gate(), reg_x[:] + reg_anc[0:1])
    quantum_circuit.append(haner_class_adder(N, n+1).to_gate().inverse(), reg_x[:] + reg_anc[:])
    quantum_circuit.append(haner_class_adder(N, n).to_gate().control(1), reg_anc[0:1] + reg_x[:] + reg_anc[1:2])
    quantum_circuit.cx(reg_x[0], reg_anc[0], ctrl_state="0")

    return quantum_circuit
