from qiskit import *
from implementations.utils.helpers import *
from implementations.arithmetic_operations.VBE.multiplier_VBE import c_mult_mod_VBE


#defines the circuit that calculates a^x mod N
def exp_mod_VBE(num_qubits: int, a: int, N: int) -> QuantumCircuit:
    """Implements the circuit operation `a^x mod N`.

    Similarly to the multiplication circuit, the exponentiation works by decomposing the operation into
    a series of smaller operations.

    .. note::
        We will take `n` as the number of bits to encode `N`.
        In Shor`s algorithm, the exponent `x` can be as big as `N^2`, this means it`s encodign can take up to `2n` bits.
    
    In this case, we decompose the exponentiation `a^x`, into a series of multiplications:

    - `a^(2^0 * x0) * a^(2^1 * x1) * ... * a^(2^(2n-1) * x(2n-1))` ; where `xi` is the i-th bit from `x`, 0 <= i < 2n;

    With that decomposition we can compute the modular exponentiation by setting the initial register to |1> and applying
    n multiplications by `a^(2^i) mod N` depending on the value of `xi`, this operation can be described as:

    If xi = 1:
    - |a^(2^0*x0 +...2^(i-1)*x(i-1)), 0> -> |a^(2^0*x0 +...2^(i-1)*x(i-1)), a^(2^0*x0 +...2^(i-1)*x(i-1)) * a^(2^i)>
    If xi = 0:
    - |a^(2^0*x0 +...2^(i-1)*x(i-1)), 0> -> |a^(2^0*x0 +...2^(i-1)*x(i-1)), a^(2^0*x0 +...2^(i-1)*x(i-1))>

    Then, to avoid accumulation of intermediate data, we run the controlled multiplication network in reverse with the value a^(-2^(i)) mod N.

    To summarise, the network consists of 3 stages:

    - Multiplication:
        - |a^(2^0*x0 +...2^(i-1)*x(i-1)), 0> -> |a^(2^0*x0 +...2^(i-1)*x(i-1)), a^(2^0*x0 +...2^i*xi)>
    - Swapping:
        - |a^(2^0*x0 +...2^(i-1)*x(i-1)), a^(2^0*x0 +...2^i*xi)> -> |a^(2^0*x0 +...2^i*xi), a^(2^0*x0 +...2^(i-1)*x(i-1))>
    - Reseting:
        - |a^(2^0*x0 +...2^i*xi), a^(2^0*x0 +...2^(i-1)*x(i-1))> -> |a^(2^0*x0 +...2^i*xi), 0>

    This is done 2n times, where at the end we'll have `a^x mod N`.


    Exemple for exp-mod circuit with 4-bit `x` exponent `a = 2` and `N = 3`:
                  _______     _______
    x0    -------|0      |---|0      |-------------------------------------------------------------------------------------------------------------------
                 |       |   |       |              _______     _______
    x1    -------|       |---|       |-------------|0      |---|0      |---------------------------------------------------------------------------------
                 |       |   |       |             |       |   |       |              _______     _______               
    x2    -------|       |---|       |-------------|       |---|       |-------------|0      |---|0      |-----------------------------------------------
                 |       |   |       |             |       |   |       |             |       |   |       |              _______     _______
    x3    -------|       |---|       |-------------|       |---|       |-------------|       |---|       |-------------|0      |---|0      |-------------
                 |       |   |       |    _____    |       |   |       |    _____    |       |   |       |    _____    |       |   |       |    _____
    oR0   ---X---|1  ->  |---|5 <-   |---|0    |---|1  ->  |---|5 <-   |---|0    |---|1  ->  |---|5 <-   |---|0    |---|1  ->  |---|5 <-   |---|0    |---
                 |   C   |   |   C   |   |  S  |   |   C   |   |   C   |   |  S  |   |   C   |   |   C   |   |  S  |   |   C   |   |   C   |   |  S  |   
    oR1   -------|2  |   |---|6  |   |---|1 W  |---|2  |   |---|6  |   |---|1 W  |---|2  |   |---|6  |   |---|1 W  |---|2  |   |---|6  |   |---|1 W  |---
                 |   M   |   |   M   |   |  A  |   |   M   |   |   M   |   |  A  |   |   M   |   |   M   |   |  A  |   |   M   |   |   M   |   |  A  |   
    cO    -------|7  U   |---|7  U   |---|  P  |---|7  U   |---|7  U   |---|  P  |---|7  U   |---|7  U   |---|  P  |---|7  U   |---|7  U   |---|  P  |--- 
                 |   L   |   |   L   |   |  P  |   |   L   |   |   L   |   |  P  |   |   L   |   |   L   |   |  P  |   |   L   |   |   L   |   |  P  |
    zR0   -------|5  T   |---|1  T   |---|2 E  |---|5  T   |---|1  T   |---|2 E  |---|5  T   |---|1  T   |---|2 E  |---|5  T   |---|1  T   |---|2 E  |---
                 |   |   |   |   |   |   |  R  |   |   |   |   |   |   |   |  R  |   |   |   |   |   |   |   |  R  |   |   |   |   |   |   |   |  R  |   
    zR1   -------|6  M   |---|2  M   |---|3____|---|6  M   |---|2  M   |---|3____|---|6  M   |---|2  M   |---|3____|---|6  M   |---|2  M   |---|3____|---
                 |   O   |   |   O   |             |   O   |   |   O   |             |   O   |   |   O   |             |   O   |   |   O   |
    anc0  -------|3  D   |---|3  D   |-------------|3  D   |---|3  D   |-------------|3  D   |---|3  D   |-------------|3  D   |---|3  D   |-------------
                 |   |   |   |   |   |             |   |   |   |   |   |             |   |   |   |   |   |             |   |   |   |   |   | 
    anc1  -------|4  3   |---|4  3   |-------------|4  3   |---|4  3   |-------------|4  3   |---|4  3   |-------------|4  3   |---|4  3   |-------------
                 |       |   |       |             |       |   |       |             |       |   |       |             |       |   |       |
    anc2  -------|8      |---|8      |-------------|8      |---|8      |-------------|8      |---|8      |-------------|8      |---|8      |-------------
                 |       |   |       |             |       |   |       |             |       |   |       |             |       |   |       |
    anc3  -------|9      |---|9      |-------------|9      |---|9      |-------------|9      |---|9      |-------------|9      |---|9      |-------------
                 |       |   |       |             |       |   |       |             |       |   |       |             |       |   |       |
    anc4  -------|10     |---|10     |-------------|10     |---|10     |-------------|10     |---|10     |-------------|10     |---|10     |-------------
                 |       |   |       |             |       |   |       |             |       |   |       |             |       |   |       |
    anc5  -------|11     |---|11     |-------------|11     |---|11     |-------------|11     |---|11     |-------------|11     |---|11     |-------------
                 |       |   |       |             |       |   |       |             |       |   |       |             |       |   |       |
    anc6  -------|12_____|---|12_____|-------------|12_____|---|12_____|-------------|12_____|---|12_____|-------------|12_____|---|12_____|-------------

    
    - Clarification:
        - oR = result register, initialized at one.
        - zR = zero register.

    Complexity:
    -
    Exponentiation operates by applying `O(n)` modular-multiplications, each one taking `O(n^2)`.

    Because of that, the network's number of gates can be described in `O(n^3)`.

    As for space, assuming `n` as the number of bits to encode `N`, we will have a total of:

    - `2n` bits for the exponent `x`.
    - `n` bits for the result register.
    - `1` final carry bit.
    - `n` temporary bits to hold partial multiplication results.
    - `3n + 1` temporary bits needed for the modular-multiplication circuit.

    Args:
        num_qubits (int): number of bits from operands.
        a (int): the base of the exponentiation.
        N (int): the modulo number, it's binary representation can have at max num_qubits.
    
    Returns:
        quantum_circuit(QuantumCirucit): the circuit implementing the operation.

    Reference: 
    -
        Quantum Networks for Elementary Arithmetic Operations.
        V. Vedral, A. Barenco, A. Ekert
    """
    x = QuantumRegister(2*num_qubits, name="x")
    oneReg = QuantumRegister(num_qubits, name="oneReg")
    zeroReg = QuantumRegister(num_qubits, name="zeroReg")
    coutReg = QuantumRegister(1, name="cout")
    anc = AncillaRegister(3*num_qubits + 1, name="anc")
    quantum_circuit = QuantumCircuit(x, oneReg, coutReg, zeroReg, anc)
    quantum_circuit.name = f"ExpMod{N}-VBE"

    #init in 1
    quantum_circuit.x(oneReg[0])

    #perform c-mult-mod and inverse n-times
    for i in range(2*num_qubits):
        a2i = (a**(2**i))%N
        ia2i = mod_inverse(a, i, N)
        quantum_circuit.append(c_mult_mod_VBE(num_qubits, a2i, N), x[i:i+1] + oneReg[:] + anc[0:num_qubits] + zeroReg[:] + coutReg[:] + anc[num_qubits:])
        quantum_circuit.append(c_mult_mod_VBE(num_qubits, ia2i, N).inverse(), x[i:i+1] + zeroReg[:] + anc[0:num_qubits] + oneReg[:] + coutReg[:] + anc[num_qubits:])
        quantum_circuit.append(swapper(num_qubits), oneReg[:] + zeroReg[:])
    return quantum_circuit