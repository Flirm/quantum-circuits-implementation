import qiskit

#returns a list with the indexes of all qubits in qregs
def get_qubits(qc: qiskit.QuantumCircuit, qregs: list[qiskit.QuantumRegister]) -> list[int]:
    bits = []
    for qreg in qregs:
        n = qc.find_bit(qreg[0]).index
        bits.extend(list(range(n, n+qreg.size)))
    return bits

#applies a not in all bits of a given register acconding to control bit
def cx_reg(num_qubits: int) -> qiskit.QuantumCircuit:
    reg = qiskit.QuantumRegister(num_qubits, name="reg")
    c = qiskit.QuantumRegister(1, name="c")
    qc = qiskit.QuantumCircuit(reg,c)
    for qubit in reg:
        qc.cx(c[0], qubit)
    return qc

#depending on the control bit state, copies n qubit register into another
def c_copy(num_qubits: int) -> qiskit.QuantumCircuit:
    c = qiskit.QuantumRegister(1, name="c")
    origin = qiskit.QuantumRegister(num_qubits, name="o")
    target = qiskit.QuantumRegister(num_qubits, name="t")
    quantum_circuit = qiskit.QuantumCircuit(c, origin, target)
    for i in range(num_qubits):
        quantum_circuit.ccx(c[0], origin[i], target[i])
    return quantum_circuit

#if control qubit is 0, zeroes out N, N is given and computed classically, else does nothing
#if N is initialized at 0, sets 0 to N
def c_set_reset(num_qubits: int, N: int) -> qiskit.QuantumCircuit:
    bit_string = bin(N)[2:]
    bit_string = bit_string.rjust(num_qubits, "0")
    circ_n = qiskit.QuantumRegister(num_qubits, name="N")
    c = qiskit.QuantumRegister(1, name="c")
    quantum_circuit = qiskit.QuantumCircuit(c, circ_n)
    quantum_circuit.x(c[0])
    for bit in range(len(bit_string)):
        if bit_string[bit] == "1":
            quantum_circuit.cx(c[0], circ_n[num_qubits-bit-1])
    quantum_circuit.x(c[0])
            
    return quantum_circuit

def set_reset(num_qubits: int, N: int) -> qiskit.QuantumCircuit:
    bit_string = bin(N)[2:]
    bit_string = bit_string.rjust(num_qubits, "0")
    circ_n = qiskit.QuantumRegister(num_qubits, name="N")
    quantum_circuit = qiskit.QuantumCircuit(circ_n)
    for bit in range(len(bit_string)):
        if bit_string[bit] == "1":
            quantum_circuit.x(circ_n[num_qubits-bit-1])
            
    return quantum_circuit