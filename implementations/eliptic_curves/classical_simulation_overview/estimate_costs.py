import math

def custo_point_add_completo(n):
    """
    Custo de UMA operação de soma de pontos em curva elíptica,
    considerando TODOS os ramos possíveis (modelo estrutural completo).
    """

    # Custos básicos
    mult = n**2
    inv = math.log2(n**2)   # ~ 2 log n
    add = n
    comp = 1

    # --- (A) Comparações ---
    custo_comp = 5 * comp

    # --- (B) Dois cálculos de lambda ---

    # lambda1 (pontos distintos)
    custo_lambda1 = (
        1 * mult +      # multiplicação
        1 * inv +       # inverso
        2 * add         # subtrações
    )

    # lambda2 (dobramento)
    custo_lambda2 = (
        4 * mult +      # multiplicações (x^2, 3x^2, 2y, produto final)
        1 * inv +       # inverso
        1 * add         # soma com a
    )

    custo_lambdas = custo_lambda1 + custo_lambda2

    # --- (C) cálculo de x ---
    custo_x = (
        1 * mult +      # lambda^2
        2 * add         # subtrações
    )

    # --- (D) cálculo de y ---
    custo_y = (
        1 * mult +      # multiplicação
        2 * add         # subtrações
    )

    # --- Total ---
    total = (
        custo_comp +
        custo_lambdas +
        custo_x +
        custo_y
    )

    return total


def custo_n_somas(n):
    """
    Custo de n somas de pontos
    """
    return n * custo_point_add_completo(n)


# -----------------------------
# Exemplo de uso
# -----------------------------
if __name__ == "__main__":
    n = 100

    custo_uma = custo_point_add_completo(n)
    custo_total = custo_n_somas(n)

    print(f"Custo de UMA soma: {custo_uma}")
    print(f"Custo de {n} somas: {custo_total}")