from qiskit import *
from arithmetic_operations.drapper.drapper_adder import draper_adder


def prepare_x_state(num_pad_qubits: int) -> QuantumCircuit:
    """Prepares the register x to a uniform superposition
    """
    reg_x = QuantumRegister(num_pad_qubits, name="reg_x")
    quantum_circuit = QuantumCircuit(reg_x)
    quantum_circuit.h(reg_x)
    return quantum_circuit


def convert_to_coset(num_op_qubits: int, num_pad_qubits: int, N: int) -> QuantumCircuit:
    """Performs |b>|x> -> |b + xN>
    After preparing x to a uniform superposition on reg_x we add 2^i * N conditioned on the i-th bit from x
    """
    reg_b = QuantumRegister(num_op_qubits+num_pad_qubits, name="reg_b")
    reg_x = QuantumRegister(num_pad_qubits, name="reg_x")
    reg_aux = QuantumRegister(1, name="aux")
    quantum_circuit = QuantumCircuit(reg_b, reg_x, reg_aux)
    quantum_circuit.append(prepare_x_state(num_pad_qubits), reg_x[:])
    for i in range(num_pad_qubits):
        quantum_circuit.append(draper_adder(num_op_qubits+num_pad_qubits, (2**i)*N, False,).control(1), reg_x[i:i+1] + reg_b[:] + reg_aux[:])
    quantum_circuit.append(prepare_x_state(num_pad_qubits).inverse(), reg_x[:])
    return quantum_circuit