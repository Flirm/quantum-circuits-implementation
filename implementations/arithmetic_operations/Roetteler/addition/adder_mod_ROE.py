"""Modular addition of two quantum registers, `|x, y> -> |x, (x + y) mod p>`.

Extracted from ``notebooks/adder_mod_ROE.ipynb``.
"""
from qiskit import QuantumCircuit, QuantumRegister

from implementations.arithmetic_operations.CDKM.adder_CDKM import adder_CDKM, comparator_CDKM
from implementations.arithmetic_operations.Haner.adder_class import haner_class_adder


def adder_mod(n: int, p: int) -> QuantumCircuit:
    """Adds two n-qubit registers modulo :attr:`p`, in place on `y`.

    Given the promise `0 <= x, y < p` and `anc` at `|00>`:

    |x, y, 00> -> |x, (x + y) mod p, 00>

    The construction has four stages:

    - `adder_CDKM` puts the `n+1`-bit sum `x + y` in `(anc[0], y)`;
    - subtracting `p` from that `n+1`-bit value leaves `anc[0]` set iff `x + y < p`;
    - controlled on `anc[0]`, `p` is added back to `y`, so `y = (x + y) mod p`;
    - `comparator_CDKM` sets `anc[0]` iff `x > y`, which happens exactly in the
      complementary case, so after the final `x` gate `anc[0]` is back to `|0>`.

    Register order:
        `x` (n) | `y` (n) | `anc` (2)

    Complexity:
    -
    `O(n log n)` gates, `2n + 2` qubits total and no clean ancilla beyond `anc`.

    Args:
        n (int): number of qubits of each operand, `n = p.bit_length()`.
        p (int): the modulus (odd).

    Returns:
        quantum_circuit(QuantumCircuit): the circuit implementing the operation.

    Reference:
    -
        Quantum resource estimates for computing elliptic curve discrete logarithms.
        Martin Roetteler, Michael Naehrig, Krysta M. Svore, Kristin Lauter. arXiv:1706.06752
    """
    reg_x = QuantumRegister(n, name="x")
    reg_y = QuantumRegister(n, name="y")
    reg_anc = QuantumRegister(2, name="anc")

    quantum_circuit = QuantumCircuit(reg_x, reg_y, reg_anc, name="adder_mod")

    quantum_circuit.append(adder_CDKM(n).to_gate(), reg_anc[1:2] + reg_x[:] + reg_y[:] + reg_anc[0:1])
    quantum_circuit.append(haner_class_adder(p, n+1).to_gate().inverse(), reg_y[:] + reg_anc[:])
    quantum_circuit.append(haner_class_adder(p, n).to_gate().control(1), reg_anc[0:1] + reg_y[:] + reg_anc[1:2])
    quantum_circuit.append(comparator_CDKM(n).to_gate(), reg_anc[1:2] + reg_y[:] + reg_x[:] + reg_anc[0:1])
    quantum_circuit.x(reg_anc[0])

    return quantum_circuit
