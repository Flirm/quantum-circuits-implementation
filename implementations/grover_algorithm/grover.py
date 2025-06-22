from qiskit import *
from qiskit.circuit.library import MCXGate, ZGate
from math import pi

def get_sat() -> tuple[int, list[list[int]]]:
    """
    To enter the clause type all the literals present in the clause separated by comma,
    if the literal is negated enter a `-` sign in front of it.
    ex: 1,3,-4 is the clause (X1 V X3 V ¬X4)
    """
    x = int(input("Enter the ammount of literals: "))
    cnf = []
    while True:
        clause = list(map(int, input("Enter a clause").split(",")))
        if clause[0] == 0:
            break
        else:
            cnf.append(clause)
    return (x, cnf)


def sat_clause_control_string(l: list[int]) -> str:
    """Given a interger list, returns the equivalent control string,
    if the number is negated returns a positive control,
    else returns the negative control.

    Exemple:
    -
    `[2,-4,-5] -> "110"`

    Args:
        l (list[int]): one SAT clause, in the format [i, j, w, ...] where i,j,w,... are the equivalent literals,
                       if the number is negative, it represents the negated literal. 

    Returns:
        c_string(str): the control string generated from the given clause to be used on the `OR` operation.
    
    """
    c_string = ""
    for i in l:
        if i > 0:
            c_string += "0"
        else:
            c_string += "1"
    return c_string[::-1]


def sat_UF(sat_x: int, sat_clauses: list[list[int]]) -> QuantumCircuit:
    x = QuantumRegister(sat_x, "x")
    anc = QuantumRegister(len(sat_clauses), "anc")
    r = QuantumRegister(1, "r")
    quantum_circuit = QuantumCircuit(x,anc,r,name="SAT-UF")
    quantum_circuit.x(anc)
    for i in range(len(sat_clauses)):
        c_string = sat_clause_control_string(sat_clauses[i])
        clause_i = MCXGate(len(sat_clauses[i]), ctrl_state=c_string)
        indexes = list(map(lambda a: abs(a)-1, sat_clauses[i]))
        quantum_circuit.append(clause_i, indexes + anc[i:i+1])
    quantum_circuit.append(MCXGate(len(sat_clauses)), anc[:] + r[:])
    return quantum_circuit


def sat_UG(bit_array: list[int], UF: QuantumCircuit) -> QuantumCircuit:
    x = QuantumRegister(bit_array[0], "x")
    anc = QuantumRegister(bit_array[1], "anc")
    r = QuantumRegister(bit_array[2], "r")
    quantum_circuit = QuantumCircuit(x,anc,r,name="SAT_UG")
    quantum_circuit.append(UF, x[:] + anc[:] + r[:])
    quantum_circuit.z(r[0])
    quantum_circuit.append(UF.inverse(), x[:] + anc[:] + r[:])
    return quantum_circuit


def inversion_by_the_mean(num_bits: int) -> QuantumCircuit:
    reg = QuantumRegister(num_bits, "reg")
    quantum_circuit = QuantumCircuit(reg, name="inversion-by-the-mean")
    quantum_circuit.h(reg)
    quantum_circuit.x(reg)
    quantum_circuit.append(ZGate().control(num_bits-1), reg[:])
    quantum_circuit.x(reg)
    quantum_circuit.h(reg)
    return quantum_circuit


def groover(bit_array: list[int], sat_clauses: list[list[int]]) -> QuantumCircuit:
    """
    bit array is the array that contains the how many bits will be used in witch register
    [5,3,1] means 5 input bits, 3 anc bits and 1 result bit.
    """
    x = QuantumRegister(bit_array[0], "x")
    anc = QuantumRegister(bit_array[1], "anc")
    r = QuantumRegister(bit_array[2], "r")  
    result = ClassicalRegister(bit_array[0], "result")
    quantum_circuit = QuantumCircuit(x,anc,r,result,name="grover-SAT")
    quantum_circuit.h(x)
    UG = sat_UG(bit_array, sat_UF(bit_array[0],sat_clauses))
    inv = inversion_by_the_mean(bit_array[0])
    num_reps = int((pi/4)*((2**bit_array[0])**(1/2)))
    for _ in range(num_reps):
        quantum_circuit.append(UG, x[:] + anc[:] + r[:])
        quantum_circuit.append(inv, x[:])
    quantum_circuit.measure(x, result)
    return quantum_circuit