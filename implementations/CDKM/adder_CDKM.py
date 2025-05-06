from qiskit import *

def qc_MAJ():
    quantum_circuit = QuantumCircuit(3)
    quantum_circuit.cx(2, 1)
    quantum_circuit.cx(2, 0)
    quantum_circuit.ccx(0, 1, 2)
    return quantum_circuit


def qc_UMA(two_version=True):
    #if argument is true, implements the 2cnot version, else, implements the 3cnot version
    #check reference
    quantum_circuit = QuantumCircuit(3)
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