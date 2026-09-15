"""Modular squaring, `|x, 0> -> |x, x^2 mod p>`.

Extracted from ``notebooks/square_mod.ipynb``.
"""
from qiskit import QuantumCircuit, QuantumRegister

from implementations.arithmetic_operations.Roetteler.addition.adder_mod_ROE import adder_mod
from implementations.arithmetic_operations.Roetteler.doubling.dbl import double_mod


def square_mod(n: int, p: int) -> QuantumCircuit:
    """Squares a register modulo :attr:`p`, accumulating into `s`.

    Given the promise `0 <= x < p`, `s` at `|0>` and `anc` at `|000>`:

    |x, 0, 000> -> |x, (x^2) mod p, 000>

    Same double-and-add schedule as :func:`qq_mult_mod`, but the second operand *is*
    `x`, so instead of a separate register the control bit `x[i]` is copied into
    `anc[2]` and used to control the addition of `x` into `s`. The copy is undone
    right after each addition, which keeps `anc[2]` clean for the next round.

    Register order:
        `x` (n) | `s` (n) | `anc` (3)

    Complexity:
    -
    `2n + 3` qubits, i.e. it saves a full n-qubit register over calling
    :func:`qq_mult_mod` with the same operand twice.

    Args:
        n (int): number of qubits of the operand, `n = p.bit_length()`.
        p (int): the modulus (odd).

    Returns:
        quantum_circuit(QuantumCircuit): the circuit implementing the operation.

    Reference:
    -
        Quantum resource estimates for computing elliptic curve discrete logarithms.
        Martin Roetteler, Michael Naehrig, Krysta M. Svore, Kristin Lauter. arXiv:1706.06752
    """
    reg_x = QuantumRegister(n, name="x")
    reg_s = QuantumRegister(n, name="s")
    reg_anc = QuantumRegister(3, name="anc")
    quantum_circuit = QuantumCircuit(reg_x, reg_s, reg_anc, name="square_mod")

    c_adder = adder_mod(n, p).to_gate().control(1)
    doubler = double_mod(p).to_gate()

    for i in range(n-1, -1, -1):
        quantum_circuit.cx(reg_x[i], reg_anc[2])
        quantum_circuit.append(c_adder, reg_anc[2:3] + reg_x[:] + reg_s[:] + reg_anc[0:2])
        if i != 0:
            quantum_circuit.append(doubler, reg_s[:] + reg_anc[0:2])
        quantum_circuit.cx(reg_x[i], reg_anc[2])

    return quantum_circuit
