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
    zero_y = QuantumRegister(num_qubits, name="0y")
    quantum_circuit = QuantumCircuit(c, x, zero_x, zero_y)

    qc_adder = mod_adder_VBE(num_qubits, N)

    #TODO: set bits
    
    #TODO: reset bits
    return quantum_circuit