from qiskit import *
from math import log2, ceil
from qiskit.circuit.library import XGate, UnitaryGate
from qiskit.circuit import Gate


def encode_table(l: list[int], size: int) -> list[str]:
    """Function encodes integers in a given list into their binary representation with `size`-bits.

    Exemple:
    -
    `[4,2,3,1,6,5,8,7] -> ['0100', '0010', '0011', '0001', '0110', '0101', '1000', '0111']`

    Args:
        l (list[int]): list of integers to be encoded.
        size (int): how many bits elements should have in it's encoding.

    Returns:
        encoded_l(list[str]): a list of strings containing the binary encoding with size-bits of the numbers in l. 
    """
    encoded_l = []
    for num in l:
        encoded_l.append((bin(num)[2:]).rjust(size,"0"))
    return encoded_l


def generate_control_strings(size: int) -> list[str]:
    """Function generates a list of binary strings from `0` to `size`.

    Exemple:
    -
    `size = 6 -> ['000', '001', '010', '011', '100', '101']`

    Args:
        size (int): number elements to be generated (list size).

    Returns:
        c_strings(list[str]): a list of binary strings from `0-size`.
    """
    c_strings = []
    string_size = ceil(log2(size))
    for i in range(size):
        c_strings.append((bin(i)[2:]).rjust(string_size,"0"))
    return c_strings


def x_data_gates(l: list[str], size: int) -> list[Gate]:
    """Generates quantum gates from a list of binary strings,
    the ih-gate action is to set initialized qubits to the i-th string in the given list.

    Exemple:
    -  
    `xor_data_gates(['0100'], 4)`

    `|0> -> |4>`
     ____
    |0   |     q0 -----
    |1 L |  =  q1 -----
    |2 0 |     q2 --X--
    |3___|     q3 -----

    Args:
        l (list[str]): a list of binary strings.
        size (int): the number of bits the gate should affect.
    
    Returns:
        circuits(list[Gate]): a list of quantum gates, the ih-gate sets `|0>` to the bit-string from the ih-element in `l`.
    """
    circuits = []
    for bit_string in l:
        qc = QuantumCircuit(size)
        for bit in range(len(bit_string)):
            if bit_string[bit] == "1":
                qc.x(abs(bit-size)-1)
        circuits.append(qc.to_gate())

    for i in range(len(circuits)):
        circuits[i].name = f"L{i}"
    return circuits


def calculate_exp_table(W: int, a: int, N: int, only_odds: bool = False) -> list[int]:
    """Given a base `a`, a modulo `N` and a window size `W` calculates the table
    `tbl[d] = a^d mod N, d = 1,2,3,...,2^W-1`

    Exemple:
    -
    `calculate_exp_table(2,3,31)` -> `[1, 3, 9, 27]`

    Args:
        W (int): window size.
        a (int): base of the exponentiation.
        N (int): modulo of the exponentiation.
        only_odds (bool): define if calculates the operation for all values of `d` or only when `d` is odd.
    
    Returns:
        exp_table(list[int]): a list with the results from the exponentiation.
    """
    exp_table = [0]*((1<<W))
    (step, start) = (2,1) if only_odds else (1,0)
    for d in range(start,(1<<W),step):
        exp_table[d] = ((a**d) % N)
    return exp_table

def calculate_mult_table(W: int, a: int, N: int) -> list[int]:
    """Given a base `a`, a modulo `N` and a window size `W` calculates the table
    `tbl[d] = a*d mod N, d = 1,2,3,...,2^W-1`

    Exemple:
    -
    `calculate_exp_table(2,3,31)` -> `[0, 2, 4, 6, 8, 10, 12, 14]`

    Args:
        W (int): window size.
        a (int): base of the multiplication.
        N (int): modulo of the operation.
    
    Returns:
        mult_table(list[int]): a list with the results from the modular multiplication.
    """
    mult_table = []
    for d in range(1<<W):
        mult_table.append((a*d) % N)
    return mult_table


def get_output_string(bin_list: list[str], size: int) -> list[str]:
    """
    separates the outputs by bit
    ex:
    `[0100, 1000, 0010, 0000, 0101]` -> `[[01000], [10001], [00100], [00001]]`
    -> `[[[0],[1],[0],[0],[0]], [[[1],[0],[0],[0],[1]], [[[0],[0],[1],[0],[0]], [[[0],[0],[0],[0],[1]]]`
    """
    new_list = ['']*size
    for i in range(size):
        for j in range(len(bin_list)):
            new_list[i] += bin_list[j][i]
    new_list = new_list[::-1]
    LL=[]
    for x in new_list:
        L=[]
        for y in x:
            L.append([int(y)])
        LL.append(L)
    return LL


def compute_lookup_table(outBits: int, l: list[int], optimization: int = 0) -> QuantumCircuit:
    """Computes the lookup-table(QROM)`[1]`, the circuit takes an input `a` and has an effect of XOR'ing 
    the corresponding a-th value of the list `l` into the `outBits` output register.

    Exemple:
    -
    W = 6
    l = any integer list of size 8

    a0 ---○----○----○----○----●----●----●----●----
          |    |    |    |    |    |    |    |
    a1 ---○----○----●----●----○----○----●----●----
          |    |    |    |    |    |    |    |
    a2 ---○----●----○----●----○----●----○----●----
          |    |    |    |    |    |    |    |
    c  ---●----●----●----●----●----●----●----●----
          |    |    |    |    |    |    |    |
    W0 --| |--| |--| |--| |--| |--| |--| |--| |---
         | |  | |  | |  | |  | |  | |  | |  | |
    W1 --| |--| |--| |--| |--| |--| |--| |--| |---
         | |  | |  | |  | |  | |  | |  | |  | |
    W2 --|L|--|L|--|L|--|L|--|L|--|L|--|L|--|L|---
         |0|  |1|  |2|  |3|  |4|  |5|  |6|  |7|
    W3 --| |--| |--| |--| |--| |--| |--| |--| |---
         | |  | |  | |  | |  | |  | |  | |  | |
    W4 --| |--| |--| |--| |--| |--| |--| |--| |---
         | |  | |  | |  | |  | |  | |  | |  | |
    W5 --|_|--|_|--|_|--|_|--|_|--|_|--|_|--|_|---

    Complexity:
    -
    Number of bits per register:

    - `o`, output register, takes `outBits` bits.
    - `w`, input register (window), takes `⌈log2|l|⌉` bits.
    - `c`, control register, takes `1` bit.

    Args:
        outBits (int): output size in bits.
        l (list[int]): list to be computed.
        optimization (int): the level of optimization the circuit should have, `default = 0`.
    
    Returns:
        quantum_circuit(QuantumCircuit): the quantum circuit implementing the lookup table (QROM).

    Reference:
    -
    [1]Encoding Electronic Spectra in Quantum Circuits with Linear T Complexity.
    Ryan Babbush, Craig Gidney, Dominic W. Berry, Nathan Wiebe, Jarrod McClean, Alexandru Paler, Austin Fowler, and Hartmut Neven
    """

    window_size = ceil(log2(len(l)))
    w = QuantumRegister(window_size, name="w")
    o = QuantumRegister(outBits, name="out")
    c = QuantumRegister(1, name="c")
    quantum_circuit = QuantumCircuit(w, c, o)
    quantum_circuit.name = "QROM"

    c_strings = generate_control_strings(len(l))
    e_table = encode_table(l, outBits)
    x_circs = x_data_gates(e_table, outBits)
    
    match optimization:
        case 0:
            for i in range(len(l)):
                get_data_circ = x_circs[i].control(window_size + 1, ctrl_state="1" + c_strings[i])
                quantum_circuit.append(get_data_circ, w[:] + c[:] + o[:])

    
    return quantum_circuit
