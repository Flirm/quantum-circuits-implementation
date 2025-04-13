#implementação do circuito de adição proposto por Vedral, Barenco e Ekert, utilizando 3n bits, onde n é número de bits de cada operando
from qiskit import *
from utils.helpers import *

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
def qc_adder_VBE(num_qubits: int) -> QuantumCircuit:
    a = QuantumRegister(num_qubits, name="a")
    b = QuantumRegister(num_qubits, name="b")
    zero = QuantumRegister(1, name="0")
    c = QuantumRegister(num_qubits, name="c")
    quantum_circuit = QuantumCircuit(a, b, zero, c)

    carry_circ = qc_carry()
    sum_circ = qc_sum()

    for i in range(num_qubits):
        quantum_circuit.compose(carry_circ, qubits=[2*num_qubits+1+i, i, num_qubits+i, 2*num_qubits+2+i if i != num_qubits-1 else 2*num_qubits], inplace=True)
    quantum_circuit.cx(num_qubits-1, 2*num_qubits-1)
    quantum_circuit.compose(sum_circ,  qubits=[3*num_qubits, num_qubits-1, 2*num_qubits-1], inplace=True)
    for i in range(num_qubits-1):
        quantum_circuit.compose(carry_circ.inverse(), qubits=[3*num_qubits-1-i, num_qubits-2-i, 2*num_qubits-2-i, 3*num_qubits-i], inplace=True)
        quantum_circuit.compose(sum_circ, qubits=[3*num_qubits-1-i, num_qubits-2-i, 2*num_qubits-2-i], inplace=True)
    return quantum_circuit


def mod_adder_VBE(num_qubits: int, N:int) -> qiskit.QuantumCircuit:
    #init work qubits and circuit
    zero = qiskit.QuantumRegister(1, name="0")
    a = qiskit.QuantumRegister(num_qubits, name="a")
    b = qiskit.QuantumRegister(num_qubits + 1, name="b")
    c = qiskit.QuantumRegister(num_qubits, name="c")
    n = qiskit.QuantumRegister(num_qubits, name="N")
    quantum_circuit = qiskit.QuantumCircuit(a, b, c, n, zero)
    
    #defining circs
    adder_circ = qc_adder_VBE(num_qubits)
    c_set_reset_n = c_set_reset(num_qubits, N)
    set_reset_n = set_reset(num_qubits, N)

    #setting N to register
    quantum_circuit.compose(set_reset_n, n[:], inplace=True)

    quantum_circuit.compose(adder_circ, a[:] + b[:] + c[:], inplace=True)
    quantum_circuit.compose(adder_circ.inverse(), n[:] + b[:] + c[:], inplace=True)

    quantum_circuit.cx(b[-1], zero[0])

    quantum_circuit.compose(c_set_reset_n, zero[:] + n[:], inplace=True)
    quantum_circuit.compose(adder_circ, n[:] + b[:] + c[:], inplace=True)
    quantum_circuit.compose(c_set_reset_n, zero[:] + n[:], inplace=True)

    quantum_circuit.compose(adder_circ.inverse(), a[:] + b[:] + c[:], inplace=True)

    quantum_circuit.x(b[-1])
    quantum_circuit.cx(b[-1], zero[0])
    quantum_circuit.x(b[-1])

    quantum_circuit.compose(adder_circ, a[:] + b[:] + c[:], inplace=True)

    
    return quantum_circuit