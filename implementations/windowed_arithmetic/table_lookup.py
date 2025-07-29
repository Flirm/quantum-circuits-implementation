from qiskit import *
from math import log2, ceil
from qiskit.circuit.library import XGate, UnitaryGate, MCXGate
from qiskit.circuit import Gate
from otimizador import executa_sintese
import re
from hypercube import cria_circuito_sintese_nova


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
    `calculate_exp_table(2,3,31,True)` -> `[0, 3, 0, 27]`

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


def tfc_str_to_qiskit(tfc_str, num_ctrl_qubits):
    """
    Converts a quantum circuit described in TFC format string to a Qiskit QuantumCircuit.

    Args:
        tfc_str (str): String containing the TFC circuit description
        num_ctrl_qubits (int): Number of control qubits in the circuit

    Returns:
        QuantumCircuit: The equivalent Qiskit circuit
    """
    qubit_map = {}
    next_qubit_index = 0
    num_classical_bits = 0
    circuit_lines = []

    lines = [line.strip() for line in tfc_str.split('\n') if line.strip()]

    in_begin_section = False
    for line in lines:
        if not line or line.startswith('#'):
            continue

        if line.startswith('.v'):
            virtual_qubits = [q.strip() for q in line.split(' ')[1].split(',')]
            for q_name in virtual_qubits:
                if q_name.startswith('b') or q_name.startswith('s'):
                    qubit_map[q_name] = next_qubit_index
                    next_qubit_index += 1
        elif line.startswith('.o'):
            output_qubit_names = [q.strip() for q in line.split(' ')[1].split(',')]
            num_classical_bits = len(output_qubit_names)
        elif line == 'BEGIN':
            in_begin_section = True
        elif line == 'END':
            in_begin_section = False
        elif in_begin_section:
            circuit_lines.append(line)

    actual_num_qubits = max(qubit_map.values()) + 1 if qubit_map else 0

    qr = QuantumRegister(actual_num_qubits, 'q')
    qc = QuantumCircuit(qr)

    print(f"Total Quantum Qubits: {actual_num_qubits}")
    print(f"Total Classical Bits (for outputs): {num_classical_bits}")
    print("Qubit Mapping:", qubit_map)

    for gate_line in circuit_lines:
        match = re.match(r'(T\d+)\s(.*)', gate_line)
        if not match:
            print(f"Warning: Could not parse line: {gate_line}")
            continue

        gate_type = match.group(1)
        qubit_names_str = match.group(2)
        qubit_names = [q.strip() for q in qubit_names_str.split(',')]

        controls = []
        target_idx = None
        control_states_str = ""

        # Process target qubit
        target_name_raw = qubit_names[-1]
        if target_name_raw.endswith("'"):
            print(f"Warning: Target qubit '{target_name_raw}' is negated. Treating as non-negated.")
            target_name = target_name_raw[:-1]
        else:
            target_name = target_name_raw

        target_idx = qubit_map.get(target_name)
        if target_idx is None:
            print(f"Error: Target qubit '{target_name}' not found in qubit map for line: {gate_line}")
            continue

        # Process control qubits
        for q_name_raw in qubit_names[:-1]:
            is_negated = False
            q_name = q_name_raw
            if q_name_raw.endswith("'"):
                is_negated = True
                q_name = q_name_raw[:-1]

            control_idx = qubit_map.get(q_name)
            if control_idx is None:
                print(f"Error: Control qubit '{q_name}' not found in qubit map for line: {gate_line}")
                continue

            controls.append(qr[num_ctrl_qubits-control_idx-1])
            control_states_str += '0' if is_negated else '1'

        # Apply gates
        if gate_type == 'T1':
            qc.x(qr[target_idx])

        elif gate_type == 'T2':
            if len(controls) != 1:
                print(f"Warning: T2 gate expects 1 control, found {len(controls)} for {gate_line}. Skipping.")
                continue
            
            if control_states_str[0] == '0':
                qc.x(controls[0])
            qc.cx(controls[0], qr[target_idx])
            if control_states_str[0] == '0':
                qc.x(controls[0])

        elif gate_type == 'T3':
            if len(controls) != 2:
                print(f"Warning: T3 gate expects 2 controls, found {len(controls)} for {gate_line}. Skipping.")
                continue
            
            temp_controls = list(controls)
            for i, control_state in enumerate(control_states_str):
                if control_state == '0':
                    qc.x(temp_controls[i])

            qc.ccx(temp_controls[0], temp_controls[1], qr[target_idx])

            for i, control_state in enumerate(control_states_str):
                if control_state == '0':
                    qc.x(temp_controls[i])

        elif gate_type.startswith('T'):
            num_involved_qubits = int(gate_type[1:])
            if len(controls) + 1 != num_involved_qubits:
                print(f"Warning: Gate {gate_type} in line '{gate_line}' implies {num_involved_qubits} qubits, but found {len(controls)+1}.")
            
            mcx_gate = MCXGate(len(controls), ctrl_state=control_states_str[::-1])
            all_involved_qubits = controls + [qr[target_idx]]
            qc.append(mcx_gate, all_involved_qubits)

        else:
            print(f"Warning: Unknown gate type {gate_type} in line: {gate_line}")

    return qc


def transform_to_permutation(orig_list: list[int], n_bits: int) -> list[int]:
    """ get unique permutation of elements from original list
    retulting list is a permutation where the last n_bits from each element represent the original value
    and the first bits are used to ensure uniqueness of the permutation.
    The first bits can also be represented as the i-th appearance of that number.
    """
    new_list = []
    appearance = {key: 0 for key in orig_list}
    for i in orig_list:
        appearance[i] += 1
        if appearance[i] <= 1:
            new_list.append(i)
        else:
            new_number = i + (1 << n_bits) * (appearance[i] - 1)
            new_list.append(new_number)
    return new_list


def complete_permutation(orig_list: list[int], n_bits: int) -> list[int]:
    """Completes the permutation by adding missing elements to the original list.
    The resulting list will contain all integers from 0 to 2^n_bits -
    """
    for i in range(1<<n_bits):
        if i not in orig_list:
            orig_list.append(i)
    return orig_list


def compute_lookup_table(window_size: int, outBits: int, l: list[int], optimization: int = 0) -> QuantumCircuit:
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

    w = QuantumRegister(window_size, name="w")
    o = QuantumRegister(outBits, name="out")
    quantum_circuit = QuantumCircuit(w, o)
    quantum_circuit.name = "QROM"

    e_table = encode_table(l, outBits)
    
    match optimization:
        case 0:
            x_circs = x_data_gates(e_table, outBits)
            c_strings = generate_control_strings(len(l))
            for i in range(len(l)):
                get_data_circ = x_circs[i].control(window_size, c_strings[i])
                quantum_circuit.append(get_data_circ, w[:] + o[:])
        case 1:
            output_str = get_output_string(e_table,outBits)
            for i in range(len(output_str)):
                tfc_circ_str = executa_sintese(n=window_size, tabela_saida=output_str[i]).__repr__()
                quantum_circuit.append(tfc_str_to_qiskit(tfc_circ_str, window_size), w[:] + o[i:i+1])
        case 2:
            #l should be the permutation list, the least significant outBits from each number in l should be the original values
            #window size can be greater than 2*outBits because of the nature of the permutation, so to ensure correct results
            #we only initialize the first 2*outBits with Haddamard gates, and only measure the first outBits
            perm_circ = cria_circuito_sintese_nova(window_size, l)
            quantum_circuit.append(perm_circ, w[:])

    return quantum_circuit