from qiskit import *
from table_lookup import compute_lookup_table
from math import log2, ceil
from implementations.arithmetic_operations.CDKM.adder_CDKM import mod_adder_CDKM_VBE


def modinv(a: int, n: int) -> int:
    t, new_t = 0, 1
    r, new_r = n, a
    while new_r != 0:
        quotient = r // new_r
        t, new_t = new_t, t - quotient * new_t
        r, new_r = new_r, r - quotient * new_r
    if r > 1:
        return None
    if t < 0:
        t = t + n
    return t


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

    assert modinv(k, N) is not None, "k must be coprime to N for the algorithm to work."

    reg_e = QuantumRegister(ne, name="input e")
    reg_a = QuantumRegister(n, name="input a")
    reg_t = QuantumRegister(n, name="target")
    reg_o = QuantumRegister(n, name="output")
    reg_temp = QuantumRegister(n, name="temp")
    reg_help = QuantumRegister(1, name="help")  # used as cOut for adder
    reg_anc = QuantumRegister(n+2, name="anc")

    quantum_circuit = QuantumCircuit(reg_e, reg_a, reg_t, reg_o, reg_temp, reg_help, reg_anc, name="win_add_mod_expVer")

    for i in range(0, ne, we):
        # Exponent - indexed factors and inverse factors .
        kes = [pow(k, 2**i * x, N) for x in range(2**we)]
        kes_inv = [modinv(x, N) for x in kes]


        for j in range(0, n, wm):
            table = [(ke * f * 2**j) % N for f in range(2**wm) for ke in kes]
            qrom = compute_lookup_table(we+wm, n, table, optimization=1)
            quantum_circuit.append(qrom, reg_e[i:i + we] + reg_a[j:j + wm] + reg_t[:])
            quantum_circuit.append(mod_adder_CDKM_VBE(n, N), reg_anc[0:1] + reg_t[:] + reg_o[:] + reg_help[:] + reg_anc[1:])
            quantum_circuit.append(qrom.inverse(), reg_e[i:i + we] + reg_a[j:j + wm] + reg_t[:])

        for j in range(0, n, wm):
            table = [(ke_inv * f * 2**j) % N for f in  range(2**wm) for ke_inv in kes_inv]
            qrom = compute_lookup_table(we+wm, n, table, optimization=1)
            quantum_circuit.append(qrom, reg_e[i:i + we] + reg_o[j:j+wm] + reg_t[:])
            quantum_circuit.append(mod_adder_CDKM_VBE(n, N).inverse(), reg_anc[0:1] + reg_t[:] + reg_a[:] + reg_help[:] + reg_anc[1:])
            quantum_circuit.append(qrom.inverse(), reg_e[i:i + we] + reg_o[j:j+wm] + reg_t[:])

        quantum_circuit.swap(reg_a, reg_o)

    return quantum_circuit