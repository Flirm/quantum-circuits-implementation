from qiskit import *
from table_lookup import compute_lookup_table
from math import log2, ceil
from win_mult_mod import win_mult_mod

def win_exp_mod(N: int, k: int, n: int, ne: int, we: int = 0, wm: int = 0) -> QuantumCircuit:
    """Algorithm works by iterating over the exponent window, every iteration multiplies the result register by k^(2^(i)*current_window).
    example: 3^11, 11 in bin = 1011, with we=2, 2 windows = [10,11], [2,3]
    1 * 3^(2^0 * 3) = 27
    27 * 3^(2^2 * 2) = 177147

    Args:
        N (int): the modulus.
        k (int): the base of the exponentiation.
        n (int): register bit size.
        ne (int): exponent bit size.
        we (int): exponentiation window size.
        wm (int): multiplication window size.

    Returns:
        quantum_circuit (QuantumCircuit): the times equal exp mod `x *= k^e mod N` circuit.
    """

    quantum_circuit = QuantumCircuit(name="win_exp_mod")

    for i in range(0, ne, we):
        #perform win_mult_mod by *k^(2^(i)*e[i:i+we])
        continue
    

    return quantum_circuit