from qiskit import *
from implementations.utils.helpers import *
from implementations.VBE.multiplier_VBE import c_mult_mod_VBE


#defines the circuit that calculates x^a mod N
def exp_mod_VBE(num_qubits: int, N: int) -> QuantumCircuit:
    quantum_circuit = QuantumCircuit()
    return quantum_circuit