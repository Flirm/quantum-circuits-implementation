from qiskit import *
from arithmetic_operations.CDKM.adder_CDKM import mod_adder_CDKM_VBE
from math import log2
from table_lookup import compute_lookup_table

def win_add_mod(N: int, w: int, n: int, k: int = 1) -> QuantumCircuit:
    """
    Args:
        N (int): the modulus.
        w (int): the addition window size.
        n (int): bit size of the operand.
        k (int): constant to multiply y.
        
    Returns:
        quantum_circuit (QuantumCircuit): the plus equal product mod `x += ky mod N` circuit.
    """
    #ideal w = lg n

    reg_y = QuantumRegister(n, 'y')
    reg_t = QuantumRegister(n, 'target')
    reg_o = QuantumRegister(n+1, 'out')
    reg_anc = QuantumRegister(n+2, 'anc')


    quantum_circuit = QuantumCircuit(reg_anc,reg_y, reg_t, reg_o, name="win_add_mod")


    #anc, a, b, cO, n, help

    #for each window i  "range(0, len(y), w)"
        #win = y[i:i + w]
        #compute the lookup table (j*k*2^i mod N for j in range(2^w))
        #target += table[win]
    for i in range(0, n, w):
        table = [j * k * 2**i % N for j in range(2**w)]
        qrom = compute_lookup_table(w, n, table, optimization=1)
        quantum_circuit.append(qrom, reg_y[i:i + w] + reg_t[:])
        quantum_circuit.append(mod_adder_CDKM_VBE(n, N), reg_anc[0:1] + reg_t[:] + reg_o[:] + reg_anc[1:])
        quantum_circuit.append(qrom.inverse(), reg_y[i:i + w] + reg_t[:])
        
        #xor qrom into targer
        #add target into out
        #undo qrom xor
        #repeat

    return quantum_circuit


