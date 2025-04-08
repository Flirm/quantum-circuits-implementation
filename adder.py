#implementação do circuito de adição proposto por Vedral, Barenco e Ekert, utilizando 3n bits, onde n é número de bits de cada operando
from qiskit import *


#qc_carry function defines a 4 qubit circuit (carryIn, a, b, carryOut) sets the carry out value accondingly for the sum of a,b,carryIn
def qc_carry() -> QuantumCircuit:
    cIn = QuantumRegister(1, name="cIn")
    a = QuantumRegister(1, name="a")
    b = QuantumRegister(1, name="b")
    cOut = QuantumRegister(1, name="cOut")
    quantum_circuit = QuantumCircuit(cIn, a, b, cOut)

    quantum_circuit.ccx(1, 2, 3)
    quantum_circuit.cx(1, 2)
    quantum_circuit.ccx(0, 2, 3)

    return quantum_circuit

#inv_qc_carry is the inverse/reversed version of qc_carry
def inv_qc_carry(quantum_circuit: QuantumCircuit, qubits: list[int]) -> QuantumCircuit:
    quantum_circuit.ccx(qubits[0], qubits[2], qubits[3]) 
    quantum_circuit.cx(qubits[1], qubits[2]) 
    quantum_circuit.ccx(qubits[1], qubits[2], qubits[3]) 
    return quantum_circuit

#qc_sum function defines a 3 qubit quantum circuit (a, b, s) and sets the value of s according to the result of the sum from a and b
def qc_sum() -> QuantumCircuit:
    c = QuantumRegister(1, name="c")
    a = QuantumRegister(1, name="a")
    b = QuantumRegister(1, name="b")
    quantum_circuit = QuantumCircuit(c, a, b)
    quantum_circuit.cx(1,2)
    quantum_circuit.cx(0,2)
    return quantum_circuit


#qc_adder funcion implements the adder circuit, (a,b) -> (a,a+b) using 3n bits, n = number of bits for each operand, operand b has an extra 0 bit to hold the final carry
#in order from least significant to most significant
#first n bits are from operand a, next n bits from b, extra bit for the last carry for b, the rest are n work bits c
#|c>|0>|b>|a>
def qc_adder(quantum_circuit: QuantumCircuit, n: int) -> QuantumCircuit:
    for i in range(n):
        quantum_circuit = qc_carry(quantum_circuit, [2*n+1+i, i, n+i, 2*n+2+i if i != n-1 else 2*n])
    quantum_circuit.cx(n-1, 2*n-1)
    quantum_circuit = qc_sum(quantum_circuit, [3*n, n-1, 2*n-1])
    for i in range(n-1):
        quantum_circuit = inv_qc_carry(quantum_circuit, [3*n-1-i, n-2-i, 2*n-2-i, 3*n-i])
        quantum_circuit = qc_sum(quantum_circuit, [3*n-1-i, n-2-i, 2*n-2-i])
    return quantum_circuit
