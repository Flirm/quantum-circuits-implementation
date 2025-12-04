from qiskit import *
from math import log2, ceil, gcd, isqrt

def prepare_registers(n: int, s: int):
    """
    prepare the x and y registers used as exponent inputs
    n is the size of the modulo in bits
    """
    size_x = ceil(n/2) + ceil(n/(2*s))
    size_y = ceil(n/(2*s))
    reg_x = QuantumRegister(size_x)
    reg_y = QuantumRegister(size_y)
    quantum_circuit = QuantumCircuit(reg_x, reg_y)
    quantum_circuit.h(reg_x)
    quantum_circuit.h(reg_y)
    return quantum_circuit

def mod_inv(a, m):
    """Retorna o inverso modular de a mod m, se existir."""
    if gcd(a, m) != 1:
        return None
    return pow(a, -1, m)

def gcd_list(xs):
    g = 0
    for v in xs:
        g = gcd(g, abs(v))
    return abs(g)

def get_h(g: int, N: int):
    return g**(N-1)

def analize_candidates(pairs: list[tuple[int, int]], r: int):
    """
    return the pairs x, y such that 
    y is inversible mod r
    """
    successes = []
    for pair in pairs:
        y = pair[1]
        if gcd(y, r) == 1:
            successes.append(pair)
    return successes

def calculate_d(pair: tuple[int, int], r: int):
    """Calculate d from d = -x*y^(-1) mod N"""
    x = pair[0]
    y = pair[1]
    d = (-x * mod_inv(y, r)) % r
    return d


def divisors(n, limit=None):
    """Gera divisores de n em ordem crescente. Se limit dado, só gera <= limit."""
    n = abs(n)
    small = []
    big = []
    i = 1
    # só até sqrt para eficiência
    while i * i <= n:
        if n % i == 0:
            small.append(i)
            j = n // i
            if j != i:
                big.append(j)
        i += 1
    for d in small:
        if limit is None or d <= limit:
            yield d
    for d in reversed(big):
        if limit is None or d <= limit:
            yield d

def recover_r(pairs, try_divisor_limit=1000000):
    """
    pairs: lista de (x', y') inteiros (medidos)
    N: opcional, se dado, tenta retornar p,q também (usado no check)
    try_divisor_limit: se G grande, só tenta divisores <= esse limite primeiro.
    Retorna lista de candidatos (R, d, consistency_fraction).
    """
    if len(pairs) < 2:
        raise ValueError("Precisa de pelo menos 2 pares")
    x1,y1 = pairs[0]
    A = []
    for (xi, yi) in pairs[1:]:
        A.append(xi*y1 - x1*yi)
    G = gcd_list(A)
    if G == 0:
        raise RuntimeError("GCD is zero (all cross products zero) — need more diverse pairs")
    candidates = []

    # Tentar divisores de G (limitado por try_divisor_limit)
    for R in divisors(G):
        # opcional: pular divisores muito grandes primeiro ou depois
        if try_divisor_limit is not None and R > try_divisor_limit and R != G:
            continue

        # procurar um par com gcd(y', R) = 1
        found = False
        for (xp, yp) in pairs:
            if gcd(yp, R) == 1:
                d = calculate_d((xp, yp), R)
                # verificar consistência com todos os pares (ou uma fração tolerável)
                ok = 0
                for (xj, yj) in pairs:
                    if (xj + d * yj) % R == 0:
                        ok += 1
                frac = ok / len(pairs)
                if frac > 0.6:   # limiar prático; ajustar conforme ruído esperado
                    candidates.append((R, d, frac))
                    found = True
                    break
        # se já achou candidato bom, podemos continuar ou parar.
    # ordenar candidatos por consistência e tamanho razoável
    candidates.sort(key=lambda t: (-t[2], t[0]))
    return G, candidates

def solve_quadratic_for_factors(N, d):
    """Resolve p+q=d+2 e pq=N e retorna (p,q)."""
    S = d + 2            # p+q
    D = S*S - 4*N        # discriminante

    root = isqrt(D)
    if root*root != D:
        raise ValueError("Discriminante não é quadrado perfeito — medições incorretas ou ruído demais.")

    p = (S - root) // 2
    q = (S + root) // 2

    if p*q != N:
        raise ValueError("Solução incorreta — talvez pegar outro par (x',y').")

    return min(p, q), max(p, q)