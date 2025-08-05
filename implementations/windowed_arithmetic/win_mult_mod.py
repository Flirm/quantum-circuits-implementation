from qiskit import *
from win_add_mod import win_add_mod

"""
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


def win_mult_mod(N: int, w: int, n: int,k: int) -> QuantumCircuit:
    
    return