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
    a = qiskit.QuantumRegister(num_qubits, name="a")
    zero = qiskit.QuantumRegister(num_qubits, name="0")
    quantum_circuit = qiskit.QuantumCircuit(c, a, zero)

    for i in range(num_qubits):
        quantum_circuit.ccx(0, i+1, num_qubits+i+1)
    return quantum_circuit