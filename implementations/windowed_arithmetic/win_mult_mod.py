from qiskit import *
from win_add_mod import win_add_mod

"""
pseudo code:
def times_equal_windowed(target: Quint, k: int, window: int):
    assert k % 2 == 1  # Even factors aren't reversible.
    k %= 2**len(target)  # Normalize factor.
    if k == 1:
        return
    table = LookupTable([
        (j * k) >> window
        for j in range(2**window)
    ])
    for i in range(0, len(target), window)[::-1]:
        w = target[i:i + window]
        target[i + window:] += table[w]

        # Recursively fix up the window.
        times_equal_windowed(w, k, window=1)
"""

#like shown in figure 6, the modular multiplication can be reduced into modular product additions, so, to do x *= k mod N
#we can simply do use the input a and the constant k in the plus equals product, the output will be a*k mod N
#then we use that result as the input and target a with k = (-k)^-1, so that the register will be 0
#we then swap the two registers, having the following result: |a> -> |a*k mod N> we use another n bit register to store partial results.


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


def win_mult_mod(N: int, w: int, n: int, k: int ) -> QuantumCircuit:

    reg_a = QuantumRegister(n, 'a')
    reg_temp = QuantumRegister(n, 'temp')
    reg_help = QuantumRegister(1, 'help') # used as cOut for adder
    reg_anc = QuantumRegister(2*n+2, 'anc')

    quantum_circuit = QuantumCircuit(reg_a, reg_temp, reg_anc, reg_help, name="win_mult_mod")

    quantum_circuit.append(win_add_mod(N, w, n, k), reg_anc[0:n+2] + reg_a[:] + reg_anc[n+2:] + reg_temp[:] + reg_help[:])
    quantum_circuit.append(win_add_mod(N, w, n, modinv(k, N)).inverse(), reg_anc[0:n+2] + reg_temp[:] + reg_anc[n+2:] + reg_a[:] + reg_help[:])
    quantum_circuit.swap(reg_a, reg_temp)

    #win add where y = reg a, out = reg temp, k = k
    #win add where y = reg temp, out = reg a, k = (-k)^-1
    #swap reg a, reg temp
    return quantum_circuit