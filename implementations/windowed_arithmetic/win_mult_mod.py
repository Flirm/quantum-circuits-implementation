from qiskit import *

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

#like shown in figure 6, the modular multiplication can be reduced into modular product additions, we simply use last result as the next window input multiplying it by k
#or the multiplicative inverse of k