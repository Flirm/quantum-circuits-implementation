"""Classical-constant adder of Häner, Roetteler and Svore.

Extracted from ``notebooks/adder_class.ipynb``. The incrementer subroutine is
reused from :mod:`implementations.arithmetic_operations.Gidney.incrementer`
instead of being redefined here.
"""
from math import ceil, floor

from qiskit import QuantumCircuit, QuantumRegister

from implementations.arithmetic_operations.Gidney.incrementer import incrementer


def carry_with_const(c: int, n: int) -> QuantumCircuit:
    """Computes the carry-out of the sum of a classical constant :attr:`c` with an n-qubit register.

    The result is XOR'ed into a single `carry` qubit. The construction borrows `n-1`
    *dirty* ancillas in an arbitrary state `|g>`, which are returned to that same
    state at the end of the computation.

    The circuit has the following effect:

    |a, g, carry> -> |a, g, carry ⊕ ((a + c) >> n)>

    Register order:
        `a` (n) | `g` (n-1) | `carry` (1)

    Args:
        c (int): the classical constant, at most `n` bits.
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
    quantum_circuit = QuantumCircuit(reg_a, reg_g, reg_carry, name="carry_with_const")

    if n == 1:
        if c & 1:
            quantum_circuit.cx(reg_a[0], reg_carry[0])
        return quantum_circuit

    quantum_circuit.cx(reg_g[n-2], reg_carry[0])

    for i in range(n - 2, -1, -1):
        if (c >> (i+1)) & 1:
            quantum_circuit.cx(reg_a[i+1], reg_g[i])
            quantum_circuit.x(reg_a[i+1])
        if i == 0: continue
        quantum_circuit.ccx(reg_g[i-1], reg_a[i+1], reg_g[i])

    if(c&1):
        quantum_circuit.ccx(reg_a[0], reg_a[1], reg_g[0])

    for i in range(n - 2):
        quantum_circuit.ccx(reg_g[i], reg_a[i+2], reg_g[i+1])

    quantum_circuit.cx(reg_g[n-2], reg_carry[0])

    for i in range(n - 3, -1, -1):
        quantum_circuit.ccx(reg_g[i], reg_a[i+2], reg_g[i+1])

    if(c&1):
        quantum_circuit.ccx(reg_a[0], reg_a[1], reg_g[0])

    for i in range(n - 1):
        if i != 0:
            quantum_circuit.ccx(reg_g[i-1], reg_a[i+1], reg_g[i])
        if (c >> (i+1)) & 1:
            quantum_circuit.x(reg_a[i+1])
            quantum_circuit.cx(reg_a[i+1], reg_g[i])

    return quantum_circuit


def sum_class_gate(c: int, n: int) -> QuantumCircuit:
    """XORs a classical constant :attr:`c` into an n-qubit register.

    This is the sum *without* carry propagation: |x> -> |x ⊕ c>. It is only a
    modular addition when the operands never generate a carry.

    Args:
        c (int): the classical constant.
        n (int): number of qubits of the register.

    Returns:
        quantum_circuit(QuantumCircuit): the circuit implementing the operation.
    """
    quantum_circuit = QuantumCircuit(n, name="sum_class")

    for i in range(n):
        if (c >> i) & 1:
            quantum_circuit.x(i)

    return quantum_circuit


def cnot_register(n: int) -> QuantumCircuit:
    """XORs a control qubit into every qubit of an n-qubit register.

    Register order:
        `a` (n) | `c` (1)

    Args:
        n (int): number of qubits of the target register.

    Returns:
        quantum_circuit(QuantumCircuit): the circuit implementing the operation.
    """
    reg_a = QuantumRegister(n, name="a")
    reg_c = QuantumRegister(1, name="c")

    quantum_circuit = QuantumCircuit(reg_a, reg_c, name="cnot_register")

    for i in range(n):
        quantum_circuit.cx(reg_c[0], reg_a[i])

    return quantum_circuit


def recursive_construction(n: int, c: int, dirty: bool = False) -> QuantumCircuit:
    """Divide-and-conquer body of :func:`haner_class_adder`.

    Splits the register in a low half (`⌈n/2⌉` qubits) and a high half (`⌊n/2⌋` qubits):
    the constant is added to the low half recursively, and the carry it produces
    drives a controlled incrementer on the high half.

    .. note::
        With :attr:`dirty` = `False` the ancilla **must** start at `|0>`; otherwise the
        controlled incrementer fires on the negated carry and the result is wrong.
        With :attr:`dirty` = `True` the ancilla may hold an arbitrary state, at the
        cost of one extra controlled incrementer and two `cnot_register` blocks.

    Register order:
        `x` (n) | `anc` (1)

    Args:
        n (int): number of qubits of the quantum operand.
        c (int): the classical constant.
        dirty (bool): whether the ancilla is allowed to start in an arbitrary state.

    Returns:
        quantum_circuit(QuantumCircuit): the circuit implementing the operation.
    """
    reg_x = QuantumRegister(n, name="x")
    reg_anc = QuantumRegister(1, name="anc")
    quantum_circuit = QuantumCircuit(reg_x, reg_anc, name="rec_class_adder")

    low_bits = ceil(n/2)
    high_bits = floor(n/2)
    low_class = c & ((1 << low_bits) - 1)
    high_class = c >> low_bits

    if n == 1:
        if c & 1:
            quantum_circuit.x(reg_x[0])
        return quantum_circuit

    #every subcircuit is appended as a Gate: a bare QuantumCircuit becomes a
    #non-unitary Instruction, which would make this circuit impossible to .control()
    carry_gate = carry_with_const(low_class, low_bits).to_gate()
    c_inc_gate = incrementer(high_bits).to_gate().control(1)

    if dirty:
        quantum_circuit.append(c_inc_gate, reg_anc[:] + reg_x[:high_bits] + reg_x[low_bits:])
        quantum_circuit.append(cnot_register(high_bits).to_gate(), reg_x[low_bits:] + reg_anc[:])

    quantum_circuit.append(carry_gate, reg_x[:low_bits] + reg_x[low_bits:2*low_bits-1] + reg_anc[:])
    quantum_circuit.append(c_inc_gate, reg_anc[:] + reg_x[:high_bits] + reg_x[low_bits:])
    quantum_circuit.append(carry_gate.inverse(), reg_x[:low_bits] + reg_x[low_bits:2*low_bits-1] + reg_anc[:])

    if dirty:
        quantum_circuit.append(cnot_register(high_bits).to_gate(), reg_x[low_bits:] + reg_anc[:])

    quantum_circuit.append(recursive_construction(low_bits, low_class, dirty).to_gate(), reg_x[:low_bits] + reg_anc[:])
    quantum_circuit.append(recursive_construction(high_bits, high_class, dirty).to_gate(), reg_x[low_bits:] + reg_anc[:])

    return quantum_circuit


def haner_class_adder(c: int, n: int, dirty: bool = False) -> QuantumCircuit:
    """Adds a classical constant :attr:`c` to an n-qubit register, modulo `2^n`.

    The circuit has the following effect:

    |x, anc> -> |(x + c) mod 2^n, anc>

    Applied in reverse it computes `|x> -> |(x - c) mod 2^n>`, which is how callers
    obtain the subtraction and the borrow flag (the MSB after an underflow).

    Register order:
        `x` (n) | `anc` (1)

    Complexity:
    -
    `O(n log n)` gates and no clean ancilla beyond the single `anc` qubit: every other
    working qubit is borrowed from the operand itself.

    Args:
        c (int): the classical constant, at most `n` bits.
        n (int): number of qubits of the quantum operand.
        dirty (bool): if `True`, `anc` may start in an arbitrary state and is restored.

    Returns:
        quantum_circuit(QuantumCircuit): the circuit implementing the operation.

    Reference:
    -
        Factoring using 2n+2 qubits with Toffoli based modular multiplication.
        Thomas Häner, Martin Roetteler, Krysta M. Svore. arXiv:1611.07995
    """
    quantum_circuit = recursive_construction(n, c, dirty)
    quantum_circuit.name = "class_adder"
    return quantum_circuit
