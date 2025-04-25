from qiskit import *
from implementations.utils.helpers import *
from implementations.VBE.multiplier_VBE import c_mult_mod_VBE


#defines the circuit that calculates a^x mod N
def exp_mod_VBE(num_qubits: int, a: int, N: int) -> QuantumCircuit:
    x = QuantumRegister(2*num_qubits, name="x")
    oneReg = QuantumRegister(num_qubits, name="oneReg")
    zeroReg = QuantumRegister(num_qubits, name="zeroReg")
    coutReg = QuantumRegister(1, name="cout")
    anc = AncillaRegister(3*num_qubits + 1, name="anc")
    quantum_circuit = QuantumCircuit(x, oneReg, coutReg, zeroReg, anc)
    quantum_circuit.name = f"ExpMod{N}-VBE"

    #init in 1
    quantum_circuit.x(oneReg[0])

    #perform c-mult-mod and inverse n-times
    for i in range(2*num_qubits):
        a2i = (a**(2**i))%N
        ia2i = mod_inverse(a, i, N)
        quantum_circuit.append(c_mult_mod_VBE(num_qubits, a2i, N), x[i:i+1] + oneReg[:] + anc[0:num_qubits] + zeroReg[:] + coutReg[:] + anc[num_qubits:])
        quantum_circuit.append(c_mult_mod_VBE(num_qubits, ia2i, N).inverse(), x[i:i+1] + zeroReg[:] + anc[0:num_qubits] + oneReg[:] + coutReg[:] + anc[num_qubits:])
        quantum_circuit.append(swapper(num_qubits), oneReg[:] + zeroReg[:])
    return quantum_circuit