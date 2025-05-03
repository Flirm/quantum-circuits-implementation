from qiskit import *
from implementations.utils.helpers import *
from implementations.VBE.adder_VBE import mod_adder_VBE

#contrlled modular multiplication proposed by Vedral, Barenco and Erkert
#given a fixed a and N, does the following effect
#|c;x,0> ->  -{ |c;x,a*x mod N> if |c>==|1>
#            \{ |c;x,x>         if |c>==|0> 
def c_mult_mod_VBE(num_qubits: int, a: int, N: int) -> QuantumCircuit:
    """Implements the circuit operation `a*x mod N`.

    This circuit works by decomposing the multiplication into a series of modular additions.

    Because `a` and `N` are given classicaly, we can decompose `a*x` into:

    - `2^0 * a * x0 + 2^1 * a * x1 + ... + 2^(n-1) * a * xn-1` ; where `xi` is the i-th bit from `x`, 0 <= i < n;

    With that decomposition in hand, we initialize a register to hold the result at `|0>`,
    then we add `2^i * a` conditioned on the state of `c` and `xi`.

    Finally, to account for the possibility of `c=0`, the state would be `|c; x, 0>`, but we want `|c; x, x>`,
    so we apply a negatively-controlled operation with `c` that copies the contents of `x` into the result register.

    The controlled modular multiplication circuit has the following effect:

    (c; x, 0) -> (c; x, a * x mod N)  if c = 1 

    (c; x, 0) -> (c; x, x)            if c = 0

    Exemple for 2-bit mult-mod circuit with `a = 2` and `N = 3`:
    

    Complexity:
    -
    Controlled multiplication operates by applying `n` modular-adders, each one taking `O(n)`.

    Because of that, the network's number of gates can be described in `O(n^2)`.

    As for space, assuming `n` as the number of bits to encode `N`, we will have a total of:

    - `1` controll-bit.
    - `n` bits for the operand `x`.
    - `n` temporary bits for the controlled addition.
    - `n` bits for the result register.
    - `1` final carry bit.
    - `2n + 1` temporary bits needed for the modular-addition circuit.

    Args:
        num_qubits (int): number of bits from operands.
        a (int): the multiplicand.
        N (int): the modulo number, it's binary representation can have at max num_qubits.
    
    Returns:
        quantum_circuit (QuantumCircuit): the circuit implementing the operation.
    
    Reference: 
    -
        Quantum Networks for Elementary Arithmetic Operations.
        V. Vedral, A. Barenco, A. Ekert
    """
    x = QuantumRegister(num_qubits, name="x")
    c = QuantumRegister(1, name="c")
    zero_x = QuantumRegister(num_qubits, name="0x")
    zero_y = QuantumRegister(num_qubits + 1, name="0y")
    anc = AncillaRegister(2*num_qubits + 1, name="anc")
    quantum_circuit = QuantumCircuit(c, x, zero_x, zero_y, anc)
    quantum_circuit.name = f"C-MultMod{N}-VBE"

    for i in range(num_qubits):
        number = ((2**i)*a)%N
        quantum_circuit.append(cc_set_reset_to_num(num_qubits, number), c[:] + x[i:i+1] + zero_x[:])
        quantum_circuit.append(mod_adder_VBE(num_qubits, N), zero_x[:] + zero_y[:] + anc[:])
        #reset N register
        quantum_circuit.append(set_reset_to(num_qubits, N), anc[num_qubits:2*num_qubits])
        quantum_circuit.append(cc_set_reset_to_num(num_qubits, number), c[:] + x[i:i+1] + zero_x[:])

    quantum_circuit.x(c[0])
    quantum_circuit.append(c_copy(num_qubits), c[:] + x[:] + zero_y[:num_qubits])
    quantum_circuit.x(c[0])
    return quantum_circuit