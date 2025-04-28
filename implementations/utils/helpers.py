import qiskit

#returns a list with the indexes of all qubits in qregs
def get_qubits(qc: qiskit.QuantumCircuit, qregs: list[qiskit.QuantumRegister]) -> list[int]:
    """Find the index location in the circuit of all qubits from all given registers.
    
    Args:
        qc (QuantumCircuit): The quantum circuit from wich the registers will be searched.
        qregs (list[QuantumRegister]): A list of quantum registers from qc, order does matter.

    Returns:
        indexList(list[int]): A list containing the interger indexes of all qubits from given registers.
    
    Examples:
        Getting the qubits from 2 registers::

            from qiskit import *
            
            a = QuantumRegister(2, "a")

            b = QuantumRegister(2, "b")

            c = QuantumRegister(2, "c")

            qc = QuantumCircuit(a, b, c)

            #Get qubits from c and a
            
            bitIndexes = get_qubits(qc, [c, a])

            #bitIndexes will look like this: [4,5,0,1]
    
    """
    bits = []
    for qreg in qregs:
        n = qc.find_bit(qreg[0]).index
        bits.extend(list(range(n, n+qreg.size)))
    return bits

#applies a not in all bits of a given register acconding to control bit
def cx_reg(num_qubits: int) -> qiskit.QuantumCircuit:
    reg = qiskit.QuantumRegister(num_qubits, name="reg")
    c = qiskit.QuantumRegister(1, name="c")
    qc = qiskit.QuantumCircuit(reg,c)
    for qubit in reg:
        qc.cx(c[0], qubit)
    return qc

#depending on the control bit state, copies n qubit register into another
def c_copy(num_qubits: int) -> qiskit.QuantumCircuit:
    """Depending on control-qubit state, copies n-qubit register into another.

    The circuit has the following effect when control-qubit is positive:

    |a,0> -> |a,a>
    
    Args:
        num_qubits (int): the number of qubits in register.

    Returns:
        quantum_curcuit(QuantumCircuit): A quantum circuit defining the operation.
    
    Exemple:
        c_copy(2)

        c:  --●--●---
        
        o0: --●--●---
              
        o1: --|--|---
              
        t0: --⊕-|---
               
        t1: -----⊕---
    """
    c = qiskit.QuantumRegister(1, name="c")
    origin = qiskit.QuantumRegister(num_qubits, name="o")
    target = qiskit.QuantumRegister(num_qubits, name="t")
    quantum_circuit = qiskit.QuantumCircuit(c, origin, target)
    quantum_circuit.name = "c-copy"
    for i in range(num_qubits):
        quantum_circuit.ccx(c[0], origin[i], target[i])
    return quantum_circuit

#if control qubit is 0, zeroes out N, N is given and computed classically, else does nothing
#if N is initialized at 0, sets 0 to N
def c_set_reset(num_qubits: int, N: int) -> qiskit.QuantumCircuit:
    """Depending on control-qubit state, resets register to `0` or does nothing
    
    The circuit has the following effect: 

    c = 0
    -
    |num> -> |0>
    
    |0> -> |num>
    
    c = 1
    -
    |num> -> |num>

    .. note::
        In particular, this circuits control-bit is controlled _negatively_.
        Keep that in mind if you want to use it and make sure to do the proper 
        not opperations to have it positively controlled.
        
        Moreover, :attr:`N` should have no more than :attr:`num_qubits` in its binary representation.

    Args:
        num_qubits (int): the number of qubits in register.
        N (int): the number in wich the register should be set/reseted to.

    Returns:
        quantum_curcuit(QuantumCircuit): A quantum circuit defining the operation.
    """   
    bit_string = bin(N)[2:]
    bit_string = bit_string.rjust(num_qubits, "0")
    circ_n = qiskit.QuantumRegister(num_qubits, name="N")
    c = qiskit.QuantumRegister(1, name="c")
    quantum_circuit = qiskit.QuantumCircuit(c, circ_n)
    quantum_circuit.x(c[0])
    for bit in range(len(bit_string)):
        if bit_string[bit] == "1":
            quantum_circuit.cx(c[0], circ_n[num_qubits-bit-1])
    quantum_circuit.x(c[0])
            
    return quantum_circuit


def set_reset_to(num_qubits: int, number: int) -> qiskit.QuantumCircuit:
    """Sets register to :attr:`number` or resets it to `0` if register contains :attr:`number`

    The circuit has the following effect: 

    |0> -> |number>

    |number> -> |0>
    
    .. note::
        :attr:`number` should have no more than :attr:`num_qubits` in its binary representation.
    
    Args:
        num_qubits (int): the number of qubits in register.
        number (int): the number in wich the register should be set/reseted to.

    Returns:
        quantum_curcuit(QuantumCircuit): A quantum circuit defining the operation.
    """
    num = qiskit.QuantumRegister(num_qubits, name="num")
    quantum_curcuit = qiskit.QuantumCircuit(num)
    quantum_curcuit.name = "set-reset"
    bit_string = bin(number)[2:]
    bit_string = bit_string.rjust(num_qubits, "0")
    for bit in range(len(bit_string)):
        if bit_string[bit] == "1":
            quantum_curcuit.x(num[num_qubits-bit-1])
    return quantum_curcuit


def cc_set_reset_to_num(num_qubits: int, num: int) -> qiskit.QuantumCircuit:
    """Depending on control-qubits state, sets register to :attr:`num` or resets it to `0` if register contains :attr:`num`

    The circuit has the following effect on register when both control-qubits are positive: 

    |0> -> |num>

    |num> -> |0>

    .. note::
        :attr:`num` should have no more than :attr:`num_qubits` in its binary representation.
      
    Args:
        num_qubtis (int): the number of qubits in register.
        num (int): the number in wich the register should be set/reseted to.

    Returns:
        quantum_curcuit(QuantumCircuit): A quantum circuit defining the operation.
    """
    c = qiskit.QuantumRegister(1, name="c")
    xi = qiskit.QuantumRegister(1, name="xi")
    target = qiskit.QuantumRegister(num_qubits, name="t")
    quantum_circuit = qiskit.QuantumCircuit(c, xi, target)
    quantum_circuit.name = "cc-set-reset"
    bit_string = bin(num)[2:]
    bit_string = bit_string.rjust(num_qubits, "0")
    for bit in range(len(bit_string)):
        if bit_string[bit] == "1":
            quantum_circuit.ccx(c[0], xi[0], target[num_qubits-bit-1])
    return quantum_circuit

#swaps two registers
def swapper(num_qubits: int) -> qiskit.QuantumCircuit:
    """Swaps bits from two n-qubit registers.

    Defines the operation |x,y> -> |y,x>

    Args:
        num_qubits (int): number of qubits from registers

    Returns:
        quantum_circuit(QuantumCircuit): A quantum circuit defining the swap operation
    
    Example:
        swapper(2)

        x0: --x---- y0

        x1: --|-x-- y1

        y0: --x-|-- x0

        y1: ----x-- x1
    """
    x = qiskit.QuantumRegister(num_qubits, name="x")
    y = qiskit.QuantumRegister(num_qubits, name="y")
    quantum_citcuit = qiskit.QuantumCircuit(x,y)
    quantum_citcuit.name = "swapper"

    for i in range(num_qubits):
        quantum_citcuit.swap(x[i], y[i])
    return quantum_citcuit

def mod_inverse(base, exponent, mod):
    """Compute the modular inverse of base^(2^exponent) mod mod"""
    
    # Compute a^(2^i) using modular exponentiation
    value = pow(base, 2**exponent, mod)

    # Compute modular inverse using Extended Euclidean Algorithm
    def extended_gcd(a, b):
        if b == 0:
            return a, 1, 0
        g, x1, y1 = extended_gcd(b, a % b)
        return g, y1, x1 - (a // b) * y1
    
    g, inverse, _ = extended_gcd(value, mod)

    if g != 1:
        raise ValueError(f"No modular inverse exists for {value} mod {mod}")
    
    return inverse % mod