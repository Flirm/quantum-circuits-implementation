"""Harness for checking that a reversible circuit computes the classical permutation it claims to.

Every arithmetic circuit in this repository is a permutation of computational basis
states, so it can be verified exhaustively for small operand sizes: prepare a basis
state, run it on the Aer simulator, and assert that the outcome is a *single*
deterministic bitstring with the expected value in each register field.

Asserting a single outcome matters: a circuit that leaves ancillas entangled with the
result still yields the right value on some shots, and only shows up here as more than
one key in the counts dictionary.
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

_SIMULATOR = AerSimulator()

#enough shots that a state split across two or more basis states is seen with
#overwhelming probability, while staying cheap (Aer samples one statevector)
DEFAULT_SHOTS = 32


class CircuitRunner:
    """Runs one circuit against many classical inputs.

    The circuit under test is transpiled once and reused, so exhaustive sweeps stay
    fast: only the input-preparation `x` gates and the measurements are rebuilt.

    Args:
        circuit (QuantumCircuit): the circuit to exercise.
    """

    def __init__(self, circuit: QuantumCircuit):
        self.num_qubits = circuit.num_qubits
        self._base = transpile(circuit, _SIMULATOR, optimization_level=0)

    def run(self, inits: list[tuple[int, int, int]], shots: int = DEFAULT_SHOTS) -> int:
        """Prepares a basis state, runs the circuit and returns the measured integer.

        Args:
            inits (list[tuple[int,int,int]]): `(start, size, value)` triples, each writing
                `value` into the qubits `[start, start+size)` in little-endian order.
            shots (int): number of shots; the outcome must be identical on all of them.

        Returns:
            measured(int): the whole register file as one integer, qubit `i` at bit `i`.

        Raises:
            AssertionError: if the final state is not a single computational basis state.
        """
        qc = QuantumCircuit(self.num_qubits, self.num_qubits)
        for start, size, value in inits:
            if not 0 <= value < (1 << size):
                raise ValueError(f"value {value} does not fit in {size} bits")
            for i in range(size):
                if (value >> i) & 1:
                    qc.x(start + i)
        qc.compose(self._base, range(self.num_qubits), inplace=True)
        qc.measure(range(self.num_qubits), range(self.num_qubits))

        counts = _SIMULATOR.run(qc, shots=shots).result().get_counts()
        if len(counts) != 1:
            raise AssertionError(
                f"circuit did not produce a single basis state for inits={inits}; "
                f"got {len(counts)} outcomes: {counts}"
            )
        return int(next(iter(counts)).replace(" ", ""), 2)


def field(measured: int, start: int, size: int) -> int:
    """Extracts the value of the qubits `[start, start+size)` from a measurement.

    Args:
        measured (int): the integer returned by :meth:`CircuitRunner.run`.
        start (int): index of the least significant qubit of the field.
        size (int): number of qubits in the field.

    Returns:
        value(int): the little-endian integer held by that slice of qubits.
    """
    return (measured >> start) & ((1 << size) - 1)
