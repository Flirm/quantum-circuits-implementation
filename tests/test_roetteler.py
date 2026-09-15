"""Correctness tests for the Roetteler et al. modular arithmetic over F_p.

These are the blocks `elc_sum_1` composes to build one elliptic-curve point addition,
so every one of them is checked against plain Python modular arithmetic, including the
restoration of all ancillas (a leaked ancilla silently breaks the uncompute in the
point-addition circuit).
"""
import unittest

from tests.sim_utils import CircuitRunner, field

from implementations.arithmetic_operations.Roetteler.addition.adder_mod_ROE import adder_mod
from implementations.arithmetic_operations.Roetteler.doubling.dbl import double_mod, mult_by_2
from implementations.arithmetic_operations.Roetteler.multiplication.qq_mult import qq_mult_mod
from implementations.arithmetic_operations.Roetteler.negation.mod_neg import mod_negation
from implementations.arithmetic_operations.Roetteler.squaring.square_mod import square_mod

#small primes whose bit length keeps the simulations cheap
PRIMES = (5, 7, 11, 13)


class TestMultBy2(unittest.TestCase):
    """|x, 0> -> |2x> over n+1 qubits (exact, no reduction)."""

    def test_exact_doubling(self):
        for n in (2, 3, 4):
            runner = CircuitRunner(mult_by_2(n))
            for x in range(1 << n):
                out = runner.run([(0, n, x), (n, 1, 0)])
                with self.subTest(n=n, x=x):
                    self.assertEqual(field(out, 0, n + 1), 2 * x)


class TestAdderMod(unittest.TestCase):
    """|x, y> -> |x, (x+y) mod p>."""

    def test_modular_addition(self):
        for p in PRIMES:
            n = p.bit_length()
            runner = CircuitRunner(adder_mod(n, p))
            for x in range(p):
                for y in range(p):
                    #register order: x (n) | y (n) | anc (2)
                    out = runner.run([(0, n, x), (n, n, y), (2 * n, 2, 0)])
                    with self.subTest(p=p, x=x, y=y):
                        self.assertEqual(field(out, n, n), (x + y) % p)
                        self.assertEqual(field(out, 0, n), x, "operand x not preserved")
                        self.assertEqual(field(out, 2 * n, 2), 0, "ancillas not restored")

    def test_inverse_is_modular_subtraction(self):
        for p in (5, 7, 11):
            n = p.bit_length()
            runner = CircuitRunner(adder_mod(n, p).inverse())
            for x in range(p):
                for y in range(p):
                    out = runner.run([(0, n, x), (n, n, y), (2 * n, 2, 0)])
                    with self.subTest(p=p, x=x, y=y):
                        self.assertEqual(field(out, n, n), (y - x) % p)
                        self.assertEqual(field(out, 2 * n, 2), 0, "ancillas not restored")


class TestDoubleMod(unittest.TestCase):
    """|x> -> |2x mod p>."""

    def test_modular_doubling(self):
        for p in PRIMES:
            n = p.bit_length()
            runner = CircuitRunner(double_mod(p))
            for x in range(p):
                #register order: x (n) | anc (2)
                out = runner.run([(0, n, x), (n, 2, 0)])
                with self.subTest(p=p, x=x):
                    self.assertEqual(field(out, 0, n), (2 * x) % p)
                    self.assertEqual(field(out, n, 2), 0, "ancillas not restored")


class TestModNegation(unittest.TestCase):
    """|x> -> |(-x) mod p| for x != 0."""

    def test_negation(self):
        for p in PRIMES:
            n = p.bit_length()
            runner = CircuitRunner(mod_negation(n, p))
            for x in range(1, p):
                #register order: x (n) | anc (1)
                out = runner.run([(0, n, x), (n, 1, 0)])
                with self.subTest(p=p, x=x):
                    self.assertEqual(field(out, 0, n), (-x) % p)
                    self.assertEqual(field(out, n, 1), 0, "ancilla not restored")

    def test_zero_maps_to_p_not_zero(self):
        """Documents the known edge case: the additive identity is not a fixed point."""
        for p in PRIMES:
            n = p.bit_length()
            runner = CircuitRunner(mod_negation(n, p))
            out = runner.run([(0, n, 0), (n, 1, 0)])
            with self.subTest(p=p):
                self.assertEqual(field(out, 0, n), p)


class TestQQMultMod(unittest.TestCase):
    """|x, y, 0> -> |x, y, (x*y) mod p>."""

    def test_modular_multiplication(self):
        for p in (5, 7):
            n = p.bit_length()
            runner = CircuitRunner(qq_mult_mod(n, p))
            for x in range(p):
                for y in range(p):
                    #register order: x (n) | y (n) | s (n) | anc (2)
                    out = runner.run([(0, n, x), (n, n, y), (2 * n, n, 0), (3 * n, 2, 0)])
                    with self.subTest(p=p, x=x, y=y):
                        self.assertEqual(field(out, 2 * n, n), (x * y) % p)
                        self.assertEqual(field(out, 0, n), x, "operand x not preserved")
                        self.assertEqual(field(out, n, n), y, "operand y not preserved")
                        self.assertEqual(field(out, 3 * n, 2), 0, "ancillas not restored")

    def test_modular_multiplication_larger_prime(self):
        """p = 11 needs 4-qubit operands; a diagonal sample keeps the runtime sane."""
        p, n = 11, 4
        runner = CircuitRunner(qq_mult_mod(n, p))
        for x in range(p):
            for y in (0, 1, x, (x + 3) % p, p - 1):
                out = runner.run([(0, n, x), (n, n, y), (2 * n, n, 0), (3 * n, 2, 0)])
                with self.subTest(p=p, x=x, y=y):
                    self.assertEqual(field(out, 2 * n, n), (x * y) % p)
                    self.assertEqual(field(out, 3 * n, 2), 0, "ancillas not restored")


class TestSquareMod(unittest.TestCase):
    """|x, 0> -> |x, (x^2) mod p>."""

    def test_modular_squaring(self):
        for p in (5, 7, 11):
            n = p.bit_length()
            runner = CircuitRunner(square_mod(n, p))
            for x in range(p):
                #register order: x (n) | s (n) | anc (3)
                out = runner.run([(0, n, x), (n, n, 0), (2 * n, 3, 0)])
                with self.subTest(p=p, x=x):
                    self.assertEqual(field(out, n, n), (x * x) % p)
                    self.assertEqual(field(out, 0, n), x, "operand not preserved")
                    self.assertEqual(field(out, 2 * n, 3), 0, "ancillas not restored")


if __name__ == "__main__":
    unittest.main()
