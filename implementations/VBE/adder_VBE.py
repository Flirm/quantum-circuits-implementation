#implementação do circuito de adição proposto por Vedral, Barenco e Ekert, utilizando 3n bits, onde n é número de bits de cada operando
from qiskit import *
from implementations.utils.helpers import *

#qc_carry function defines a 4 qubit circuit (carryIn, a, b, carryOut) sets the carry out value accondingly for the sum of a,b,carryIn
def qc_carry() -> QuantumCircuit:
    """Implements the bitwise carry operation, given the `carry in` and two bits `a` and `b`
    defines the `carry out`.

    cIn:  ------●--
                |
    a:    --●-●-|--
            | | | 
    b:    --●-⨁-●--
            |    |
    cOut: --⨁---⨁--
    
    Returns:
        quantum_circuit(QuantumCircuit): the circuit implementing the operation.
    """
    cIn = QuantumRegister(1, name="cIn")
    a = QuantumRegister(1, name="a")
    b = QuantumRegister(1, name="b")
    cOut = QuantumRegister(1, name="cOut")
    quantum_circuit = QuantumCircuit(cIn, a, b, cOut)
    quantum_circuit.name = "carry"

    quantum_circuit.ccx(1, 2, 3)
    quantum_circuit.cx(1, 2)
    quantum_circuit.ccx(0, 2, 3)

    return quantum_circuit

#qc_sum function defines a 3 qubit quantum circuit (a, b, s) and sets the value of s according to the result of the sum from a and b
def qc_sum() -> QuantumCircuit:
    """Implements the bitwise sum operation between two bits `c` and `a` and stores the result in `b`.

    c: ----●--
           | 
    a: -●--|--
        |  |
    b: -⨁-⨁--
    
    Returns:
        quantum_circuit(QuantumCircuit): the circuit implementing the operation.
    """
    c = QuantumRegister(1, name="c")
    a = QuantumRegister(1, name="a")
    b = QuantumRegister(1, name="b")
    quantum_circuit = QuantumCircuit(c, a, b)
    quantum_circuit.name = "sum"
    quantum_circuit.cx(1,2)
    quantum_circuit.cx(0,2)
    return quantum_circuit


#qc_adder funcion implements the adder circuit, (a,b) -> (a,a+b) using 3n bits, n = number of bits for each operand, operand b has an extra 0 bit to hold the final carry
#in order from least significant to most significant
#first n bits are from operand a, next n bits from b, extra bit for the last carry for b, the rest are n work bits c
#|c>|0>|b>|a>
def adder_VBE(num_qubits: int) -> QuantumCircuit:
    """Implements the circuit to sum two :attr:`n-bit` numbers.

    It works by first calculating all carry bits, applyign n carry gates taking the i-th c[i], a[i], b[i], c[i+1] as entries.

    The last carry-bit is stored in b.

    After that, using the calculated carry bits we apply n sum gates tanking c[i], a[i], b[i] as entries.

    Finally, we apply the inverse carry gates to reset the state of the c-bits to 0.

    The plain adder circuit has the following effect:

    (a,b) -> (a,a+b)

    If applied in reverse:

    (a,b) -> (a,b-a)            if b >= a

    (a,b) -> (a,2^(n+1)-(a-b))  if a > b

    
    Exemple for 2-bit sum plain adder circuit:

            -----                         -----    -----
    c0: ---|  -> |-----------------------|  <- |--|  -> |---
           |  c  |                       |  c  |  |  s  |
    a0: ---|  a  |-----------------------|  a  |--|  u  |---
           |  r  |                       |  r  |  |  m  |
    b0: ---|  r  |-----------------------|  r  |--|     |---
           |  y  |   -----       -----   |  y  |   -----
    c1: ---|     |--|  -> |-----|  -> |--|     |------------
            -----   |  c  |     |  s  |   -----
    a1:-------------|  a  |--●--|  u  |---------------------
                    |  r  |  |  |  m  |
    b1:-------------|  r  |--⨁-|     |---------------------
                    |  y  |      -----
    cO:-------------|     |---------------------------------
                     -----

    Complexity:
    -
    The network depth as well as number of gates can be described in `O(n)`.

    As for space, assuming `n` as the number of bits to encode the largest operand, we will have a total of:

    - `2n` bits for operands `a` and `b`
    - `1` bit for the final carry
    - `n` bits for other carries

    Args:
        num_qubits (int): number of bits from operands.

    Returns:
        quantum_circuit(QuantumCircuit): the circuit implementing the operation.

    Reference: 
    -
        Quantum Networks for Elementary Arithmetic Operations.
        V. Vedral, A. Barenco, A. Ekert
    """
    a = QuantumRegister(num_qubits, name="a")
    b = QuantumRegister(num_qubits, name="b")
    zero = QuantumRegister(1, name="0")
    c = QuantumRegister(num_qubits, name="c")
    quantum_circuit = QuantumCircuit(a, b, zero, c)
    quantum_circuit.name = "Adder-VBE"

    carry_circ = qc_carry()
    sum_circ = qc_sum()

    for i in range(num_qubits):
        quantum_circuit.compose(carry_circ, qubits=[2*num_qubits+1+i, i, num_qubits+i, 2*num_qubits+2+i if i != num_qubits-1 else 2*num_qubits], inplace=True)
    quantum_circuit.cx(num_qubits-1, 2*num_qubits-1)
    quantum_circuit.compose(sum_circ,  qubits=[3*num_qubits, num_qubits-1, 2*num_qubits-1], inplace=True)
    for i in range(num_qubits-1):
        quantum_circuit.compose(carry_circ.inverse(), qubits=[3*num_qubits-1-i, num_qubits-2-i, 2*num_qubits-2-i, 3*num_qubits-i], inplace=True)
        quantum_circuit.compose(sum_circ, qubits=[3*num_qubits-1-i, num_qubits-2-i, 2*num_qubits-2-i], inplace=True)
    return quantum_circuit

#returns a circuit that calculates (a+b)%N, where N is given and computed classically, a and b both have n qubits
#it is promissed that 0 <= a,b < N
def mod_adder_VBE(num_qubits: int, N:int) -> QuantumCircuit:
    """Implements the circuit to sum two :attr:`n-bit` numbers modulo :attr:`N`.

    For the circuit to work properly it is given as promisse that `0 <= a,b < N`

    .. note::
        This version has some differences when compared to `[1]`, this is because the original description has some errors
        in it, this implementation corrects them.

    We can divide the circuit's working in 4 parts:

    - Use the plain adder to sum `a` and `b` and store the result in `b`.
    - Use the reverse adder with the registers `(N, b)` as input:
        - If `N > a + b`, it will cause underflow.
        - Check the most significant bit for underflow and set the `controll-bit` accordingly.
    - Now we check the `controll-bit` state:
        - If negative, there was no underflow, this means we don't need to undo the operation, so we zero out the N register.
        - If positive, there was underflow, this means `a + b` was smaller than `N` and we need to undo the operation.
    - After checking the `controll-bit` and doing setting the N register we apply the plain adder with `(N, b)` again as input:
        - Remember: if `c-bit` was negative, `N` will have `|0>`, else it will be `N`.
    - Lastly, to reset the controll-bit to 0, we take the inverse adder with `(a, b)` as input:
        - It will cause underflow if `a > b`, and this will only be case when `b` reg is `a+b-N`, meaning the c-bit is already at `0`.
        - If there is no underflow, it means `b` content is `a+b`, this only happends when the `c-bit` is set to `1`.
        - To reset the `c-bit`, we can use a negatively controlled `cnot` at `b`'s most significant bit targetign the `c-bit`.
    - Then, we just apply the plain adder with `(a, b)` as input to undo the effects from the last inverse adder. 

    The plain adder circuit has the following effect:

    (a,b) -> (a, a+b)   if a+b < N

    (a,b) -> (a, a+b-N) if a+b >= N

    If applied in reverse:

    (a,c) -> (a, c-a)   if c >= a

    (a,c) -> (a, N+c-a) if c < a

    Exemple mod-adder with 2-bit operands and `N = 3`:
                 _____                                _____           _____
    a0    ------|0    |------------------------------|0    |---------|0    |---
                |     |                              |     |         |     |
    a1    ------|1    |------------------------------|1    |---------|1    |---
                |  -> |    _____            _____    | <-  |         |  -> |
    b0    ------|2 A  |---|2    |----------|2    |---|2 A  |---------|2 A  |---
                |  D  |   |     |          |     |   |  D  |         |  D  |
    b1    ------|3 D  |---|3    |----------|3    |---|3 D  |---------|3 D  |---
                |  E  |   | <-  |          |  -> |   |  E  |         |  E  |
    cO    ------|4 R  |---|4 A  |--●-------|4 A  |---|4 R  |--X-●-X--|4 R  |---
                |     |   |  D  |  |       |  D  |   |     |    |    |     |
    anc0  ------|5    |---|5 D  |--|-------|5 D  |---|5    |----|----|5    |---
                |     |   |  E  |  |       |  E  |   |     |    |    |     |
    anc1  ------|6____|---|6 R  |--|-------|6 R  |---|6____|----|----|6____|---
                          |     |  |   _   |     |   _          |
    N0    -X--------------|0    |--|--| |--|0    |--| |---------|--------------
                          |     |  |  | |  |     |  | |         |
    N1    -X--------------|1____|--|--|_|--|1____|--|_|---------|--------------
                                   |   |             |          |
    0     -------------------------⨁-X-●-X---------X-●-X-------⨁--------------


    Complexity:
    -
    The network depth as well as number of gates can be described in `O(n)`.
    
    For space, assuming `n` as the number of bits to encode `N`, we will have a total of:

    - `3n` bits for `a`, `b` and `N`.
    - `1` bit for the final carry.
    - `1` bit to manage controlled operatons.
    - `n` extra bits for the plain adder.
    
    Args:
        num_qubits (int): number of bits from operands.
        N (int): the modulo number, it's binary representation can have at max num_qubits.

    Returns:
        quantum_circuit(QuantumCircuit): the circuit implementing the operation.

    Reference: 
    -
        [1] Quantum Networks for Elementary Arithmetic Operations.
        V. Vedral, A. Barenco, A. Ekert
    """
    #init work qubits and circuit
    zero = QuantumRegister(1, name="0")
    a = QuantumRegister(num_qubits, name="a")
    b = QuantumRegister(num_qubits + 1, name="b")
    c = QuantumRegister(num_qubits, name="c")
    n = QuantumRegister(num_qubits, name="N")
    quantum_circuit = QuantumCircuit(a, b, c, n, zero)
    quantum_circuit.name = f"AdderMod{N}-VBE"

    #defining circs
    adder_circ = adder_VBE(num_qubits)
    c_set_reset_n = c_set_reset(num_qubits, N)
    set_reset_n = set_reset_to(num_qubits, N)

    #setting N to register
    quantum_circuit.compose(set_reset_n, n[:], inplace=True)

    quantum_circuit.compose(adder_circ, a[:] + b[:] + c[:], inplace=True)
    quantum_circuit.compose(adder_circ.inverse(), n[:] + b[:] + c[:], inplace=True)

    quantum_circuit.cx(b[-1], zero[0])

    quantum_circuit.compose(c_set_reset_n, zero[:] + n[:], inplace=True)
    quantum_circuit.compose(adder_circ, n[:] + b[:] + c[:], inplace=True)
    quantum_circuit.compose(c_set_reset_n, zero[:] + n[:], inplace=True)

    quantum_circuit.compose(adder_circ.inverse(), a[:] + b[:] + c[:], inplace=True)

    quantum_circuit.x(b[-1])
    quantum_circuit.cx(b[-1], zero[0])
    quantum_circuit.x(b[-1])

    quantum_circuit.compose(adder_circ, a[:] + b[:] + c[:], inplace=True)

    return quantum_circuit