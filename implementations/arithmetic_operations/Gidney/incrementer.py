from qiskit import *

def sub_carry_gate():
    quantum_circuit1 = QuantumCircuit(3)
    quantum_circuit1.cx(0,1)
    quantum_circuit1.cx(2,0)
    quantum_circuit1.ccx(0,1,2)

    quantum_circuit2 = QuantumCircuit(3)
    quantum_circuit2.ccx(0,1,2)
    quantum_circuit2.cx(2,0)
    quantum_circuit2.cx(2,1)

    return (quantum_circuit1, quantum_circuit2)

def incrementer(n:int):
    reg_v = QuantumRegister(n, name="v")
    reg_g = QuantumRegister(n, name="g")
    quantum_circuit = QuantumCircuit(reg_g, reg_v)

    for i in range(n): 
        quantum_circuit.cx(reg_g[0], reg_v[i])
        if i != 0: quantum_circuit.x(reg_g[i])
    quantum_circuit.x(reg_v[n-1])

    sub_gate1, sub_gate2 = sub_carry_gate()

    for i in range(n-1):
        quantum_circuit.append(sub_gate1, reg_g[i:i+1] + reg_v[i:i+1] + reg_g[i+1:i+2])

    quantum_circuit.cx(reg_g[n-1], reg_v[n-1])

    for i in range(n-2, -1, -1):
        quantum_circuit.append(sub_gate2, reg_g[i:i+1] + reg_v[i:i+1] + reg_g[i+1:i+2])

    for i in range(1, n): quantum_circuit.x(reg_g[i])

    for i in range(n-1):
        quantum_circuit.append(sub_gate1, reg_g[i:i+1] + reg_v[i:i+1] + reg_g[i+1:i+2])

    quantum_circuit.cx(reg_g[n-1], reg_v[n-1])

    for i in range(n-2, -1, -1):
        quantum_circuit.append(sub_gate2, reg_g[i:i+1] + reg_v[i:i+1] + reg_g[i+1:i+2])

    for i in range(n): 
        quantum_circuit.cx(reg_g[0], reg_v[i])

    return quantum_circuit
    