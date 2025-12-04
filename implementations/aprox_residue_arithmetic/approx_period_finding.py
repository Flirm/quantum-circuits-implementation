from qiskit import *
from math import sqrt, ceil, log2

def prepare_s(error: int, N: int, f: int):
    """
    prepare the mask register s into a uniform superposition in the first S*N bits
    S is defined as a value proportional to the modular deviation
    if we sum this prepared value into the approximated exponential function output
    we should fix the problem with the periodicity
    """
    S = sqrt(error)
    size = int(log2(ceil(S*N))) + 1
    reg_s = QuantumRegister(f, "reg_mask")
    quantum_circuit = QuantumCircuit(reg_s)
    quantum_circuit.h(reg_s[0:size])
    return quantum_circuit

