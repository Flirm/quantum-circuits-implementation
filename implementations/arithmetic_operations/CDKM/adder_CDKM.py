from qiskit import *
from implementations.utils.helpers import *

def qc_MAJ() -> QuantumCircuit:
    """
    
    q0 -----⨁--●-----
            |   |
    q1 --⨁-|---●-----
         |  |   |
    q2 --●--●---⨁----

    Returns:
        quantum_circuit (QuantumCircuit): the circuit implementing the operation.
    """
    quantum_circuit = QuantumCircuit(3)
    quantum_circuit.name = "MAJ"
    quantum_circuit.cx(2, 1)
    quantum_circuit.cx(2, 0)
    quantum_circuit.ccx(0, 1, 2)
    return quantum_circuit

#if argument is true, implements the 2cnot version, else, implements the 3cnot version
#check reference
def qc_UMA(two_version: bool=True) -> QuantumCircuit:
    """
    
    - 2-CNOT verison:

    q0 --●--⨁--●--
         |  |  |
    q1 --●--|--⨁--
         |  |
    q2 --⨁--●-----


    - 3-CNOT version:

    q0 ------●--●------⨁-----
             |  |      |
    q1 --⨁--⨁--●--⨁--|--⨁--
                |      |  |
    q2 ---------⨁-----●--●---


    Returns:
        quantum_circuit (QuantumCircuit): the circuit implementing the operation.
    """
    quantum_circuit = QuantumCircuit(3)
    quantum_circuit.name = "UMA"
    if two_version:
        quantum_circuit.ccx(0, 1, 2)
        quantum_circuit.cx(2, 0)
        quantum_circuit.cx(0, 1)
    else:
        quantum_circuit.x(1)
        quantum_circuit.cx(0, 1)
        quantum_circuit.ccx(0, 1, 2)
        quantum_circuit.x(1)
        quantum_circuit.cx(2, 0)
        quantum_circuit.cx(2, 1)
    return quantum_circuit


def adder_CDKM(num_qubits: int, modulo_2n: bool=False) -> QuantumCircuit:
    """

    Complexity:
    -
    For space, assuming `n` as the number of bits to encode the largest operand, we will have a total of:

    - `1` bit for carryIn/Ancilla
    - `2n` bits for operands `a` and `b`
    - If operation is not `modulo 2^n`:
        - `1` bit for carryOut

    Args:
        num_qubits (int): number of bits from operands.
        modulo_2n (bool): indicates if operation is made modulo 2^n or not.

    Returns:
        quantum_circuit (QuantumCircuit): the circuit implementing the operation.

    Reference:
    -
        A new quantum ripple-carry addition circuit. 
        Steven A. Cuccaro, Thomas G. Draper, Samuel A. Kutin, David Petrie Moulton
    """
    c = QuantumRegister(1, name="c")
    a = QuantumRegister(num_qubits, name="a")
    b = QuantumRegister(num_qubits, name="b")
    if not modulo_2n:
        z = QuantumRegister(1, name="z") 
        quantum_circuit = QuantumCircuit(c,a,b,z, name="Adder-CDKM")
    else:
        quantum_circuit = QuantumCircuit(c,a,b, name="Adder-CDKM-MOD2^n")
    
    #appended as gates so that callers can .control() circuits built on top of this one
    maj = qc_MAJ().to_gate()
    uma = qc_UMA().to_gate()

    quantum_circuit.append(maj, c[0:1] + b[0:1] + a[0:1])

    for i in range(1, num_qubits):
        quantum_circuit.append(maj, a[i-1:i] + b[i:i+1] + a[i:i+1])

    if not modulo_2n: quantum_circuit.cx(a[-1], z[0])

    for i in range(num_qubits-1, 0, -1):
        quantum_circuit.append(uma, a[i-1:i] + b[i:i+1] + a[i:i+1])

    quantum_circuit.append(uma, c[0:1] + b[0:1] + a[0:1])
    return quantum_circuit


def comparator_CDKM(num_qubits: int) -> QuantumCircuit:
    """Compares two n-qubit registers, flagging `b > a` on the `s` qubit.

    Reuses the MAJ chain of :func:`adder_CDKM` on the complement of `a`: the carry-out
    of `~a + b` is set exactly when `b > a`. Both operands are restored by running the
    MAJ chain backwards (no UMA), so this is a pure comparison with no side effect
    besides the flag.

    The circuit has the following effect, given `anc` at `|0>`:

    |anc, a, b, s> -> |anc, a, b, s ⊕ [b > a]>

    Register order:
        `anc` (1) | `a` (n) | `b` (n) | `s` (1)

    Args:
        num_qubits (int): number of qubits of each operand.

    Returns:
        quantum_circuit (QuantumCircuit): the circuit implementing the operation.

    Reference:
    -
        A new quantum ripple-carry addition circuit.
        Steven A. Cuccaro, Thomas G. Draper, Samuel A. Kutin, David Petrie Moulton
    """
    reg_anc = QuantumRegister(1, name="anc")
    reg_a = QuantumRegister(num_qubits, name="a")
    reg_b = QuantumRegister(num_qubits, name="b")
    reg_s = QuantumRegister(1, name="s")
    quantum_circuit = QuantumCircuit(reg_anc, reg_a, reg_b, reg_s, name="comparator_CDKM")

    maj = qc_MAJ().to_gate()

    quantum_circuit.compose(complement(num_qubits), reg_a[:], inplace=True)

    quantum_circuit.append(maj, [reg_anc[0], reg_b[0], reg_a[0]])

    for i in range(1, num_qubits):
        quantum_circuit.append(maj, [reg_a[i-1], reg_b[i], reg_a[i]])

    quantum_circuit.cx(reg_a[num_qubits-1], reg_s[0])

    for i in range(num_qubits-1, 0, -1):
        quantum_circuit.append(maj.inverse(), [reg_a[i-1], reg_b[i], reg_a[i]])

    quantum_circuit.append(maj.inverse(), [reg_anc[0], reg_b[0], reg_a[0]])

    quantum_circuit.compose(complement(num_qubits), reg_a[:], inplace=True)

    return quantum_circuit


def mod_adder_CDKM_VBE(num_qubits: int, N: int) -> QuantumCircuit:
    anc = QuantumRegister(1, name="anc")
    a = QuantumRegister(num_qubits, name="a")
    b = QuantumRegister(num_qubits, name="b")
    cO = QuantumRegister(1, name="cO")
    n = QuantumRegister(num_qubits, name="N")
    help = QuantumRegister(1, name="help")
    quantum_circuit = QuantumCircuit(anc, a, b, cO, n, help, name=f"AdderMod{N}-CDKM-VBE")

    quantum_circuit.append(set_reset_to(num_qubits, N), n[:])

    quantum_circuit.append(adder_CDKM(num_qubits), anc[:] + a[:] + b[:] + cO[:])
    quantum_circuit.append(adder_CDKM(num_qubits).inverse(), anc[:] + n[:] + b[:] + cO[:])

    quantum_circuit.cx(cO[0], help[0])

    quantum_circuit.append(c_set_reset(num_qubits, N), help[:] + n[:])
    quantum_circuit.append(adder_CDKM(num_qubits), anc[:] + n[:] + b[:] + cO[:])
    quantum_circuit.append(c_set_reset(num_qubits, N), help[:] + n[:])

    quantum_circuit.append(adder_CDKM(num_qubits).inverse(), anc[:] + a[:] + b[:] + cO[:])

    quantum_circuit.x(cO[0])
    quantum_circuit.cx(cO[0], help[0])
    quantum_circuit.x(cO[0])

    quantum_circuit.append(adder_CDKM(num_qubits), anc[:] + a[:] + b[:] + cO[:])

    quantum_circuit.append(set_reset_to(num_qubits, N), n[:])

    return quantum_circuit