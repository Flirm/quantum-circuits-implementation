from qiskit import *
from prime_fetcher import find_P_with_robust_search
from math import log2, lcm
from arithmetic_operations.drapper.drapper_adder import adder_mod
from windowed_arithmetic.win_mult_mod import win_mult_mod

# ----------- pre-computed values ----------- #

def get_primes(N: int, bits_e: int, f: int):
    P, L, d, max_ell_used = find_P_with_robust_search(N, bits_e, f,
                                    ell_start=None,
                                    ell_max_increase=6,
                                    top_fraction=0.25,
                                    mix_fraction=0.06,
                                    limit_primes_read=None,
                                    overshoot_limit=3,
                                    greedy_attempts=400,
                                    local_iter=300)

    return P, L, d, max_ell_used

def get_constants(L: int, P: list[int], N: int, f: int):
    u = get_ujs(P, L)
    C = get_Cjk(u, N, L, f)
    return u, C


def get_ujs(P, L):
    """
    Calcula os cofatores u_j = (L/p_j) * inv(L/p_j mod p_j) mod L
    """
    u_list = []
    for p in P:
        Lj = L // p
        inv = pow(Lj, -1, p)
        u = (Lj * inv)
        u_list.append(u)
    return u_list


def get_Cjk(u_list, N, L, f):
    """
    Calcula os fatores C_{j,k} conforme (eq. 21):
    C_{j,k} = (((u_j << k) mod L mod N) >> t) mod (N >> t)
    """
    C = []
    nbits = int(log2(N)) + 1
    t = nbits - f
    N_trunc = N >> t

    for j, u in enumerate(u_list):
        Cj = []
        for k in range(f):  # bits mais significativos a considerar
            val = ((u << k) % L) % N
            val = val >> t
            val = val % N_trunc
            Cj.append(val)
        C.append(Cj)
    return C


# ----------- quantum alg ----------- #

def naive_bit_shift(shift: int, reg_size: int, left: bool = True):
    """
    shifts the register by (shift) truncating values if necessary,
    shift direction defined by (left)
    """
    quantum_circuit = QuantumCircuit(reg_size)

    if not left:
        for i in range(0, reg_size-shift):
            quantum_circuit.swap(i, shift+i)
        quantum_circuit.reset(range(reg_size-shift,reg_size))
    else:
        for i in range(0, reg_size-shift):
            quantum_circuit.swap(i, shift+i)
        quantum_circuit.reset(range(shift))

    return quantum_circuit

def approx_mod_exp(N:int, f:int, g:int, exp_size:int):
    """
    N: mod
    g: exp base for g^e mod N
    exp_size: exponent size in bits
    f: bits to keep in during approximation ~loglogN
    """
    n = int(log2(N)) + 1
    P, L, d, max_ell = get_primes(N, exp_size, f) #prime set, pset product, P mod deviation, max bits used from p in P
    t = n - f #number of bits to be truncated
    u, C = get_constants(L, P, N, f) #get lists containing constans uj and Cjk

    assert d < 2**(-f), "Modular deviation should be less than 2^(-f)"
    assert L == lcm(*P) and L >= N**exp_size and (L % N) < (N >> f), "L should be a prime prod, grater than N^m and its modulo N should be less than the f truncation of N"

    #quantum circuit definition
    #sizes may change later
    reg_e = QuantumRegister(exp_size, "reg_e") # exponent reg
    reg_out = QuantumRegister(n, "reg_out") # output reg
    reg_res = QuantumRegister(n, "reg_res") # residue reg
    reg_aux = QuantumRegister(3*n+3, "reg_aux") # auxiliar reg, may change later
    quantum_circuit = QuantumCircuit(reg_e, reg_out, reg_res, reg_aux)

    for j, p in enumerate(P):
        # sets residue reg to 1
        quantum_circuit.reset(reg_res)
        quantum_circuit.x(reg_res[0])

        # calculates rj through iterating in r_jk accumulating in qres
        for k in range(exp_size):
            r_jk = pow(g, 1<<k, N) % p #calculates current residue
            #control mult mod qres = (qres * r_jk) % p
            #controlled by reg_exp[k] 
            mult = win_mult_mod(N, 1, reg_res.size, r_jk)
            quantum_circuit.append(mult, reg_res[:] + reg_aux[:])
        
        # calculates out by the given formula V = (sum(j to lenP)sum(k to ell)rjk*Cjk) mod (N>>t)
        for k in range(max_ell):
            #do control add mod q_out = (q_out + Cjk) % (N >> t)
            #controlled by reg_res[k]
            c = C[j][k]
            adder = adder_mod(reg_res.size, c, N>>t, True)
            quantum_circuit.append(adder, reg_res[k:k+1] + reg_out[:] + reg_aux[0:2])

    # final bit shift, Q_total << t, can be deduced in post processing
    bit_shift = naive_bit_shift(t, reg_out.size)
    quantum_circuit.append(bit_shift, reg_out[:])

    return quantum_circuit