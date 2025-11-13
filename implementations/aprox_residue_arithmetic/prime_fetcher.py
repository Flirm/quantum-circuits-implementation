import math, random, time
from fractions import Fraction
from sympy import primerange, mod_inverse

# ---------- utilitários ----------
def modular_deviation(L, N):
    """Δ_N(L) = |L/N - round(L/N)| usando Fraction para precisão exata"""
    frac = Fraction(L, N)
    return abs(frac - round(frac))

def estimate_required_primes(N, m, ell):
    """Estimativa aproximada de |P| = ceil(m * log2(N) / ell)"""
    nbits = math.log2(N)
    return math.ceil(m * nbits / ell)

# ---------- geração de pool ----------
def generate_primes_up_to_ell_bits(ell, limit_count=None):
    """Gera primos < 2^ell. Limit_count limita quantidade lida (útil para ell grande)."""
    limit = (1 << ell) - 1
    if limit_count is None:
        return list(primerange(2, limit + 1))
    else:
        out = []
        for p in primerange(2, limit + 1):
            out.append(p)
            if len(out) >= limit_count:
                break
        return out

def generate_primes_biased_by_value(ell, top_fraction=0.3, mix_fraction=0.05, limit_count=None):
    """
    Gera pool com viés para os maiores:
    - top_fraction = fração superior do intervalo em valor (ex: 0.25 = últimos 25% valores)
    - mix_fraction = fração dos primos abaixo do threshold a amostrar (para ajuste fino)
    - limit_count = limitar geração total (opcional)
    Retorna pool ordenado decrescentemente (maiores primeiro).
    """
    min_val = 2
    max_val = (1 << ell) - 1
    range_w = max_val - min_val + 1
    threshold_value = max_val - int(range_w * top_fraction) + 1

    all_primes = generate_primes_up_to_ell_bits(ell, limit_count=limit_count)
    big_primes = [p for p in all_primes if p >= threshold_value]
    small_primes = [p for p in all_primes if p < threshold_value]

    mix_count = max(0, int(len(small_primes) * mix_fraction))
    mix_sample = random.sample(small_primes, mix_count) if mix_count > 0 else []

    pool = sorted(big_primes, reverse=True) + sorted(mix_sample, reverse=True)
    # ensure uniqueness
    seen = set()
    pool_unique = []
    for p in pool:
        if p not in seen:
            seen.add(p)
            pool_unique.append(p)
    return pool_unique

# ---------- seleção gulosa ----------
def greedy_select_primes(pool, N, m, overshoot_limit=4):
    """
    Seleciona primos na ordem do pool até atingir L >= N^m.
    Limita overshoot evitando L > N^(m*overshoot_limit).
    Retorna (L, P) ou (None,None).
    """
    target = N ** m
    max_L = N ** (m * overshoot_limit)
    L = 1
    P = []
    for p in pool:
        L *= p
        P.append(p)
        if L >= target:
            if L > max_L and len(P) > 1:
                # remove último e continue
                L //= p
                P.pop()
                continue
            return L, P
    return None, None

# ---------- local search / heurísticas ----------
def local_swap_improve(N, L, P, pool, max_swaps=3, iter_limit=200):
    """
    Tenta melhorar Δ trocando até `max_swaps` primos entre P e candidatos de pool.
    Retorna (best_L, best_P, best_d).
    Usa uma busca estocástica: tenta combinações aleatórias de swaps.
    """
    best_L = L
    best_P = P[:]
    best_d = modular_deviation(L, N)
    candidates = [c for c in pool if c not in P]
    if not candidates:
        return best_L, best_P, best_d

    # tentativa 1: trocar um por um (determinístico)
    for i in range(len(P)-1, max(0, len(P)-7)-1, -1):  # prioriza swaps nos últimos ~7 elementos
        p_old = P[i]
        for cand in candidates:
            L_new = (best_L // p_old) * cand
            d_new = modular_deviation(L_new, N)
            if 0 < d_new < best_d:
                best_d = d_new; best_L = L_new; best_P = P[:]; best_P[i] = cand

    # tentativa estocástica: swaps múltiplos aleatórios
    start_time = time.time()
    tries = 0
    while tries < iter_limit and time.time() - start_time < 2.0:
        tries += 1
        k = random.randint(1, max_swaps)
        idxs = random.sample(range(len(P)), k)
        cand_idxs = random.sample(range(len(candidates)), k if k <= len(candidates) else len(candidates))
        P_new = P[:]
        L_new = best_L
        # perform swaps
        for ii, ci in zip(idxs, cand_idxs):
            old = P_new[ii]
            cand = candidates[ci]
            L_new = (L_new // old) * cand
            P_new[ii] = cand
        d_new = modular_deviation(L_new, N)
        if 0 < d_new < best_d:
            best_d = d_new; best_L = L_new; best_P = P_new[:]
    return best_L, best_P, best_d

# ---------- main search ----------
def find_P_with_robust_search(N, m, f,
                              ell_start=None, ell_max_increase=6,
                              top_fraction=0.3, mix_fraction=0.03,
                              limit_primes_read=None,
                              overshoot_limit=3,
                              greedy_attempts=300,
                              local_iter=300):
    """
    Busca por P tais que 0 < Δ_N(L) <= 2^-f, tentando aumentar ell se necessário.
    Retorna (P,L,delta,ell_used) ou (best_found,...).
    Parâmetros explicados no código acima.
    """
    if ell_start is None:
        ell_start = math.ceil(math.log2(math.log2(N)))
    limiar = Fraction(1, 2**f)
    best_overall = (None, None, Fraction(1,1), None)  # (P,L,d,ell)

    for ell_inc in range(0, ell_max_increase+1):
        ell = ell_start + ell_inc
        print(f"[info] testando ell={ell} ... (estimativa |P| ≈ {estimate_required_primes(N,m,ell)})")
        pool = generate_primes_biased_by_value(ell, top_fraction=top_fraction,
                                               mix_fraction=mix_fraction, limit_count=limit_primes_read)
        if not pool:
            print(f"[warn] nenhum primo gerado para ell={ell}")
            continue

        # check if product of pool can in principle reach target
        prod_all = 1
        for p in pool:
            prod_all *= p
            if prod_all >= N**m:
                break
        if prod_all < N**m:
            print(f"[info] produto de todo pool insuficiente para N^m — aumentando ell")
            continue

        # várias tentativas greedy com pequenas permutações
        for attempt in range(greedy_attempts):
            # partially shuffle lower part to keep bias but explore variations
            head = pool[:max(1, int(len(pool)*0.6))]  # keep top 60% order
            tail = pool[max(1, int(len(pool)*0.6)):]
            random.shuffle(tail)
            candidate_pool = head + tail

            L, P = greedy_select_primes(candidate_pool, N, m, overshoot_limit=overshoot_limit)
            if L is None:
                continue
            d = modular_deviation(L, N)

            # immediate accept if meets strict criterion (and not zero)
            if 0 < d <= limiar:
                print(f"[ok] encontrado ell={ell}, tentativa {attempt+1}, Δ={float(d):.3e}, |P|={len(P)}")
                return P, L, float(d), ell

            # try local improve
            L2, P2, d2 = local_swap_improve(N, L, P, candidate_pool, max_swaps=4, iter_limit=local_iter)
            if 0 < d2 <= limiar:
                print(f"[ok local] encontrado ell={ell}, tentativa {attempt+1}, Δ={float(d2):.3e}, |P|={len(P2)}")
                return P2, L2, float(d2), ell

            # update best overall if improved
            if d != 0 and d < best_overall[2]:
                best_overall = (P, L, d, ell)

        print(f"[info] não encontrou para ell={ell} em {greedy_attempts} tentativas. melhor Δ até agora = {float(best_overall[2]):.3e}")

    # fim loop ell
    if best_overall[0] is not None:
        Pbest, Lbest, dbest, ellbest = best_overall
        print(f"[best] melhor solução parcialmente encontrada: ell={ellbest}, |P|={len(Pbest)}, Δ={float(dbest):.3e}")
        print(f"Primos encontrados: {Pbest}")
        return Pbest, Lbest, float(dbest), ellbest

    print("[fail] não foi possível encontrar P satisfatório dentro dos limites especificados.")
    return None, None, None, None


if __name__ == "__main__":
    N = 10**12        # N
    m = 8             # número de multiplicações/expoente efetivo
    f = 10            # bits mantidos (limiar 2^-f)
    # Parâmetros de controle da busca:
    ell_start = None          # None -> calcula log2(log2(N))
    ell_max_increase = 6
    top_fraction = 0.25       # priorizar últimos 25% do intervalo [2..2^ell-1]
    mix_fraction = 0.06       # amostra pequena de primos menores para ajuste
    limit_primes_read = None  # limite práticos (ex: 10000) para ell grande
    overshoot_limit = 3
    greedy_attempts = 400
    local_iter = 300

    res = find_P_with_robust_search(N, m, f,
                                    ell_start=ell_start,
                                    ell_max_increase=ell_max_increase,
                                    top_fraction=top_fraction,
                                    mix_fraction=mix_fraction,
                                    limit_primes_read=limit_primes_read,
                                    overshoot_limit=overshoot_limit,
                                    greedy_attempts=greedy_attempts,
                                    local_iter=local_iter)

    P, L, d, ell_used = res
    if P:
        print("\n--- Resultado final ---")
        print("ell_used:", ell_used)
        print("len(P):", len(P))
        print("Δ_N(L):", d)
        print("primos:", P)
        print("L:", L)
    else:
        print("Nenhuma solução encontrada. Tente ajustar parâmetros (ver recomendações).")
