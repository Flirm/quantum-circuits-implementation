from qiskit import *
from table_lookup import compute_lookup_table
from math import log2, ceil

def win_exp_mod(N: int, base: int, n: int, ne: int, we: int = 0, wm: int = 0) -> QuantumCircuit:
    """
    Args:
        N (int): the modulus.
        base (int): the base of the exponentiation.
        ne (int): exponent bit size.
        we (int): exponentiation window size.
        wm (int): multiplication window size.

    Returns:
        quantum_circuit (QuantumCircuit): the times equal exp mod `x *= k^e mod N` circuit.
    """

    n = int(log2(N)) + 1
    num_w = ceil(n / we)
    

    return