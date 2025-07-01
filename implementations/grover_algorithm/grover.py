from qiskit import *
from qiskit.circuit.library import MCXGate, ZGate, QFT
from math import pi, sin
from qiskit_aer import AerSimulator
from qiskit import transpile

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


def grover(bit_array: list[int], sat_clauses: list[list[int]]) -> QuantumCircuit:
    """Grover Operator
    bit array is the array that contains the how many bits will be used in witch register
    [5,3,1] means 5 input bits, 3 anc bits and 1 result bit.
    """
    x = QuantumRegister(bit_array[0], "x")
    anc = QuantumRegister(bit_array[1], "anc")
    r = QuantumRegister(bit_array[2], "r")
    quantum_circuit = QuantumCircuit(x,anc,r,name="grover-SAT")
    UG = sat_UG(bit_array, sat_UF(bit_array[0],sat_clauses).to_gate()).to_gate()
    inv = inversion_by_the_mean(bit_array[0]).to_gate()
    quantum_circuit.append(UG, x[:] + anc[:] + r[:])
    quantum_circuit.append(inv, x[:])
    return quantum_circuit


def grover_search(bit_arr: list[int], fnc: list[list[int]], m: int = 1) -> QuantumCircuit:
    """
    bit array [num_literals, num_anc, num_result]
    """
    G = grover(bit_arr, fnc)
    x = QuantumRegister(bit_arr[0], "x")
    anc = QuantumRegister(bit_arr[1], "anc")
    r = QuantumRegister(bit_arr[2], "r")
    result = ClassicalRegister(bit_arr[0], "result")
    quantum_circuit = QuantumCircuit(x,anc,r,result)
    quantum_circuit.h(x)
    num_reps = int((pi/4)*(((2**bit_arr[0])/m)**(1/2)))
    for i in range(num_reps):
        quantum_circuit.append(G, x[:] + anc[:] + r[:])
    quantum_circuit.measure(x,result)
    return quantum_circuit


def grover_counting(bit_arr: list[int], fnc: list[list[int]]) -> QuantumCircuit:
    G = grover(bit_arr, fnc)
    x = QuantumRegister(bit_arr[0], "x")
    anc = QuantumRegister(bit_arr[1], "anc")
    r = QuantumRegister(bit_arr[2], "r")
    p = QuantumRegister(bit_arr[3], "p")
    result = ClassicalRegister(bit_arr[3], "result")
    quantum_circuit = QuantumCircuit(p,x,anc,r,result)
    quantum_circuit.h(p)
    quantum_circuit.h(x)
    num_reps = bit_arr[3]
    for i in range(num_reps):
        quantum_circuit.append(G.power(2**i).control(1), p[i:i+1] + x[:] + anc[:] + r[:])
    quantum_circuit.append(QFT(bit_arr[3], inverse=True), p[:])
    quantum_circuit.measure(p, result)
    return quantum_circuit


def get_search_solution(GS: QuantumCircuit) -> str:
    simulator_aer = AerSimulator()
    qc_aer = transpile(GS, backend=simulator_aer)
    job = simulator_aer.run(qc_aer, shots=(1<<15))
    job_result = job.result()
    counts = job_result.get_counts(qc_aer)
    value = counts.most_frequent()
    return value


def get_counting_solution(bits: list[int], GC: QuantumCircuit) -> float:
    """bits [n_literals, n_precision_bits]
    """
    simulator_aer = AerSimulator()
    qc_aer = transpile(GC, backend=simulator_aer)
    job = simulator_aer.run(qc_aer, shots=(1<<15))
    job_result = job.result()
    counts = job_result.get_counts(qc_aer)
    measured_value = int(counts.most_frequent(),2)

    n = 2**bits[0]
    theta = 2*pi*measured_value/(2**bits[1])
    m = n*(sin(theta/2))**2
    print(f"M = {m}")
    print(f"N = {n}")
    print(f"Number of solutions: ~{n-m}")
    return n-m