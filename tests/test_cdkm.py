"""Correctness tests for the CDKM ripple-carry adder and the comparator built on it."""
import unittest

from tests.sim_utils import CircuitRunner, field

from implementations.arithmetic_operations.CDKM.adder_CDKM import (
    adder_CDKM,
    comparator_CDKM,
)


class TestAdderCDKM(unittest.TestCase):
    """|c, a, b, z> -> |c, a, a+b mod 2^n, z ^ carry>."""

    def test_addition_with_carry_out(self):
        for n in (1, 2, 3, 4):
            runner = CircuitRunner(adder_CDKM(n))
            for a in range(1 << n):
                for b in range(1 << n):
                    #register order: c (1) | a (n) | b (n) | z (1)
                    out = runner.run([(0, 1, 0), (1, n, a), (1 + n, n, b), (1 + 2 * n, 1, 0)])
                    with self.subTest(n=n, a=a, b=b):
                        self.assertEqual(field(out, 1 + n, n), (a + b) % (1 << n))
                        self.assertEqual(field(out, 1 + 2 * n, 1), (a + b) >> n, "wrong carry out")
                        self.assertEqual(field(out, 1, n), a, "operand a not preserved")
                        self.assertEqual(field(out, 0, 1), 0, "carry-in ancilla not restored")

    def test_modulo_2n_variant_has_no_carry_qubit(self):
        for n in (2, 3):
            circuit = adder_CDKM(n, modulo_2n=True)
            self.assertEqual(circuit.num_qubits, 2 * n + 1)
            runner = CircuitRunner(circuit)
            for a in range(1 << n):
                for b in range(1 << n):
                    out = runner.run([(0, 1, 0), (1, n, a), (1 + n, n, b)])
                    with self.subTest(n=n, a=a, b=b):
                        self.assertEqual(field(out, 1 + n, n), (a + b) % (1 << n))
                        self.assertEqual(field(out, 1, n), a, "operand a not preserved")

    def test_inverse_subtracts(self):
        for n in (2, 3):
            runner = CircuitRunner(adder_CDKM(n).inverse())
            for a in range(1 << n):
                for b in range(1 << n):
                    out = runner.run([(0, 1, 0), (1, n, a), (1 + n, n, b), (1 + 2 * n, 1, 0)])
                    with self.subTest(n=n, a=a, b=b):
                        self.assertEqual(field(out, 1 + n, n), (b - a) % (1 << n))


class TestComparatorCDKM(unittest.TestCase):
    """|anc, a, b, s> -> |anc, a, b, s ^ [b > a]>, both operands restored."""

    def test_flags_b_greater_than_a(self):
        for n in (1, 2, 3, 4):
            runner = CircuitRunner(comparator_CDKM(n))
            for a in range(1 << n):
                for b in range(1 << n):
                    #register order: anc (1) | a (n) | b (n) | s (1)
                    out = runner.run([(0, 1, 0), (1, n, a), (1 + n, n, b), (1 + 2 * n, 1, 0)])
                    with self.subTest(n=n, a=a, b=b):
                        self.assertEqual(field(out, 1 + 2 * n, 1), int(b > a))
                        self.assertEqual(field(out, 1, n), a, "operand a not preserved")
                        self.assertEqual(field(out, 1 + n, n), b, "operand b not preserved")
                        self.assertEqual(field(out, 0, 1), 0, "ancilla not restored")


if __name__ == "__main__":
    unittest.main()
