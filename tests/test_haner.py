"""Correctness tests for the Häner classical-constant adder family."""
import unittest

from tests.sim_utils import CircuitRunner, field

from implementations.arithmetic_operations.Gidney.incrementer import incrementer
from implementations.arithmetic_operations.Haner.adder_class import (
    carry_with_const,
    haner_class_adder,
)
from implementations.arithmetic_operations.Haner.mod_adder_class import (
    comparator_class,
    haner_mod_class_adder,
)


class TestIncrementer(unittest.TestCase):
    """|g, v> -> |g, v+1 mod 2^n>, with g borrowed dirty and restored."""

    def test_increments_and_restores_dirty_ancillas(self):
        for n in (1, 2, 3, 4):
            runner = CircuitRunner(incrementer(n))
            for g in (0, (1 << n) - 1, 1 % (1 << n)):
                for v in range(1 << n):
                    #register order: g (n) | v (n)
                    out = runner.run([(0, n, g), (n, n, v)])
                    with self.subTest(n=n, g=g, v=v):
                        self.assertEqual(field(out, n, n), (v + 1) % (1 << n))
                        self.assertEqual(field(out, 0, n), g, "dirty ancillas not restored")


class TestCarryWithConst(unittest.TestCase):
    """|a, g, carry> -> |a, g, carry ^ ((a+c) >> n)>."""

    def test_carry_out_matches_classical(self):
        for n in (1, 2, 3):
            for c in range(1 << n):
                runner = CircuitRunner(carry_with_const(c, n))
                for a in range(1 << n):
                    for g in (0, (1 << (n - 1)) - 1):
                        #register order: a (n) | g (n-1) | carry (1)
                        out = runner.run([(0, n, a), (n, n - 1, g), (2 * n - 1, 1, 0)])
                        with self.subTest(n=n, c=c, a=a, g=g):
                            self.assertEqual(field(out, 2 * n - 1, 1), (a + c) >> n)
                            self.assertEqual(field(out, 0, n), a, "operand not preserved")
                            self.assertEqual(field(out, n, n - 1), g, "dirty ancillas not restored")


class TestHanerClassAdder(unittest.TestCase):
    """|x> -> |(x + c) mod 2^n>."""

    def test_clean_ancilla(self):
        for n in (1, 2, 3, 4):
            for c in range(1 << n):
                runner = CircuitRunner(haner_class_adder(c, n))
                for x in range(1 << n):
                    #register order: x (n) | anc (1)
                    out = runner.run([(0, n, x), (n, 1, 0)])
                    with self.subTest(n=n, c=c, x=x):
                        self.assertEqual(field(out, 0, n), (x + c) % (1 << n))
                        self.assertEqual(field(out, n, 1), 0, "ancilla not restored")

    def test_dirty_ancilla(self):
        """The dirty variant must give the same result for either ancilla state."""
        for n in (2, 3, 4):
            for c in range(1 << n):
                runner = CircuitRunner(haner_class_adder(c, n, dirty=True))
                for x in range(1 << n):
                    for anc in (0, 1):
                        out = runner.run([(0, n, x), (n, 1, anc)])
                        with self.subTest(n=n, c=c, x=x, anc=anc):
                            self.assertEqual(field(out, 0, n), (x + c) % (1 << n))
                            self.assertEqual(field(out, n, 1), anc, "ancilla not restored")

    def test_inverse_subtracts(self):
        """Running the adder backwards is the subtraction used by every modular block."""
        for n in (2, 3, 4):
            for c in range(1 << n):
                runner = CircuitRunner(haner_class_adder(c, n).inverse())
                for x in range(1 << n):
                    out = runner.run([(0, n, x), (n, 1, 0)])
                    with self.subTest(n=n, c=c, x=x):
                        self.assertEqual(field(out, 0, n), (x - c) % (1 << n))


class TestComparatorClass(unittest.TestCase):
    """|x, g, carry> -> |x, g, carry ^ [x < c]>."""

    def test_flags_x_less_than_c(self):
        for n in (2, 3, 4):
            for c in range(1 << n):
                runner = CircuitRunner(comparator_class(c, n))
                for x in range(1 << n):
                    #register order: a (n) | g (n-1) | carry (1)
                    out = runner.run([(0, n, x), (n, n - 1, 0), (2 * n - 1, 1, 0)])
                    with self.subTest(n=n, c=c, x=x):
                        self.assertEqual(field(out, 2 * n - 1, 1), int(x < c))
                        self.assertEqual(field(out, 0, n), x, "operand not preserved")


class TestHanerModClassAdder(unittest.TestCase):
    """|x> -> |(x + c) mod p>, the workhorse of the elliptic-curve point addition."""

    def test_modular_addition(self):
        for p in (5, 7, 11, 13):
            n = p.bit_length()
            for c in range(p):
                runner = CircuitRunner(haner_mod_class_adder(c, n, p))
                for x in range(p):
                    #register order: x (n) | g (n-1) | anc (1)
                    out = runner.run([(0, n, x), (n, n - 1, 0), (2 * n - 1, 1, 0)])
                    with self.subTest(p=p, c=c, x=x):
                        self.assertEqual(field(out, 0, n), (x + c) % p)
                        self.assertEqual(field(out, n, n - 1), 0, "dirty register not restored")
                        self.assertEqual(field(out, 2 * n - 1, 1), 0, "ancilla not restored")

    def test_inverse_is_modular_subtraction(self):
        """`elc_sum_1` relies on the inverse to subtract the classical coordinates."""
        for p in (5, 7, 11):
            n = p.bit_length()
            for c in range(p):
                runner = CircuitRunner(haner_mod_class_adder(c, n, p).inverse())
                for x in range(p):
                    out = runner.run([(0, n, x), (n, n - 1, 0), (2 * n - 1, 1, 0)])
                    with self.subTest(p=p, c=c, x=x):
                        self.assertEqual(field(out, 0, n), (x - c) % p)


if __name__ == "__main__":
    unittest.main()
