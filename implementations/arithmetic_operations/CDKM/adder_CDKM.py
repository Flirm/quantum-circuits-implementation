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
    """
    c = QuantumRegister(1, name="c")
    a = QuantumRegister(num_qubits, name="a")
    b = QuantumRegister(num_qubits, name="b")
    if not modulo_2n:
        z = QuantumRegister(1, name="z") 
        quantum_circuit = QuantumCircuit(c,a,b,z, name="Adder-CDKM")
    else:
        quantum_circuit = QuantumCircuit(c,a,b, name="Adder-CDKM-MOD2^n")
    
    quantum_circuit.append(qc_MAJ(), c[0:1] + b[0:1] + a[0:1])

    for i in range(1, num_qubits):
        quantum_circuit.append(qc_MAJ(), a[i-1:i] + b[i:i+1] + a[i:i+1])

    if not modulo_2n: quantum_circuit.cx(a[-1], z[0])
        
    for i in range(num_qubits-1, 0, -1):
        quantum_circuit.append(qc_UMA(), a[i-1:i] + b[i:i+1] + a[i:i+1])
        
    quantum_circuit.append(qc_UMA(), c[0:1] + b[0:1] + a[0:1])
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