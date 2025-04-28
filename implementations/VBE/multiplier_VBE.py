from qiskit import *
from implementations.utils.helpers import *
from implementations.VBE.adder_VBE import mod_adder_VBE

#contrlled modular multiplication proposed by Vedral, Barenco and Erkert
#given a fixed a and N, does the following effect
#|c;x,0> ->  -{ |c;x,a*x mod N> if |c>==|1>
#            \{ |c;x,x>         if |c>==|0> 
def c_mult_mod_VBE(num_qubits: int, a: int, N: int) -> QuantumCircuit:
    x = QuantumRegister(num_qubits, name="x")
    c = QuantumRegister(1, name="c")
    zero_x = QuantumRegister(num_qubits, name="0x")
    zero_y = QuantumRegister(num_qubits + 1, name="0y")
    anc = AncillaRegister(2*num_qubits + 1, name="anc")
    quantum_circuit = QuantumCircuit(c, x, zero_x, zero_y, anc)
    quantum_circuit.name = f"C-MultMod{N}-VBE"

    for i in range(num_qubits):
        number = ((2**i)*a)%N
        quantum_circuit.append(cc_set_reset_to_num(num_qubits, number), c[:] + x[i:i+1] + zero_x[:])
        quantum_circuit.append(mod_adder_VBE(num_qubits, N), zero_x[:] + zero_y[:] + anc[:])
        #reset N register
        quantum_circuit.append(set_reset_to(num_qubits, N), anc[num_qubits:2*num_qubits])
        quantum_circuit.append(cc_set_reset_to_num(num_qubits, number), c[:] + x[i:i+1] + zero_x[:])

    quantum_circuit.x(c[0])
    quantum_circuit.append(c_copy(num_qubits), c[:] + x[:] + zero_y[:num_qubits])
    quantum_circuit.x(c[0])
    return quantum_circuit