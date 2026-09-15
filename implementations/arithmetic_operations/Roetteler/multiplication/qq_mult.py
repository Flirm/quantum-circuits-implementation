"""Quantum-quantum modular multiplication, `|x, y, 0> -> |x, y, x*y mod p>`.

Extracted from ``notebooks/qq_mult.ipynb``.
"""
from qiskit import QuantumCircuit, QuantumRegister

from implementations.arithmetic_operations.Roetteler.addition.adder_mod_ROE import adder_mod
from implementations.arithmetic_operations.Roetteler.doubling.dbl import double_mod


def qq_mult_mod(n: int, p: int) -> QuantumCircuit:
    """Multiplies two quantum registers modulo :attr:`p`, accumulating into `s`.

    Given the promise `0 <= x, y < p`, `s` at `|0>` and `anc` at `|00>`:

    |x, y, 0, 00> -> |x, y, (x * y) mod p, 00>

    Uses the MSB-first double-and-add schedule: for each bit of `x` from the most
    significant down, `y` is added into `s` conditioned on that bit, and `s` is doubled
    between iterations. Both operands are left untouched.

    Register order:
        `x` (n) | `y` (n) | `s` (n) | `anc` (2)

    Complexity:
    -
    `n` controlled modular additions and `n-1` modular doublings, so `O(n^2 log n)`
    gates in `3n + 2` qubits.

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
    reg_s = QuantumRegister(n, name="s")
    reg_anc = QuantumRegister(2, name="anc")

    quantum_circuit = QuantumCircuit(reg_x, reg_y, reg_s, reg_anc, name="qq_mult_mod")

    c_adder = adder_mod(n, p).to_gate().control(1)
    doubler = double_mod(p).to_gate()

    for i in range(n-1, -1, -1):
        quantum_circuit.append(c_adder, reg_x[i:i+1] + reg_y[:] + reg_s[:] + reg_anc[:])
        if i != 0:
            quantum_circuit.append(doubler, reg_s[:] + reg_anc[:])

    return quantum_circuit
