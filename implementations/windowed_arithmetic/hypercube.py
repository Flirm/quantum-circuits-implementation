"""
Cídigo original feito por: Guilherme da Hora (https://github.com/Kourggos)
"""

from qiskit import QuantumCircuit, QuantumRegister
from table_lookup import calculate_exp_table, calculate_mult_table

def porta(k, x, y, pi, limite):
    """
    Realiza uma troca na permutação baseada em uma "porta" e imprime a operação.

    Args:
        k (int): Número de bits.
        x (int): Valor atual na permutação a ser trocado.
        y (int): Posição do bit (1-based) que define a porta.
        pi (list): A lista (vetor) da permutação.
        limite (int): O deslocamento para limitar a busca inicial no array.
    """
    # Calcula o valor a ser trocado (aux) usando XOR para inverter o bit na posição y.
    # y-1 porque a indexação de bits é 0-based na programação, mas 1-based na lógica do problema.
    z = 1 << (y - 1)
    aux = x ^ z

    # --- Imprime a representação da porta, como "T(1*0)" ---
    # Constrói uma lista de caracteres para a representação binária
    representacao_porta = []
    for i in range(k - 1, -1, -1):
        if i == y - 1:
            representacao_porta.append('*')
        elif (x & (1 << i)):
            representacao_porta.append('1')
        else:
            representacao_porta.append('0')
            
    #print(f"T({''.join(representacao_porta)[::-1]})")

    # --- Realiza a troca na permutação ---
    # Encontra o índice de 'aux' na parte "não resolvida" da lista e o substitui por 'x'.
    # O slice pi[:-limite] corresponde à busca nos primeiros pow(2,k)-limite elementos.
    # Nota: Em Python, é mais fácil usar o método index().
    block_index = -1
    try:
        # Busca apenas na parte relevante da lista, que diminui a cada iteração do hipercubo
        if limite > 0:
            block_index = pi.index(aux, 0, len(pi) - limite)
        else:
            block_index = pi.index(aux)
        pi[block_index] = x
    except ValueError:
        # Ocorre se o valor não for encontrado. O código C original não trata este erro.
        # print(f"Aviso: valor {aux} não encontrado na sublista designada.")
        return

    # Encontra o índice de 'x' (que não seja o que acabamos de colocar) e o substitui por 'aux'.
    # Isso completa a troca.
    try:
        for i in range(len(pi)):
            if pi[i] == x and i != block_index:
                pi[i] = aux
                break
    except ValueError:
        pass # Ignora se não encontrar

    return f"{''.join(representacao_porta)}"[::-1]

def hipercubo(k, vet_s):
    """
    Processa a permutação para ordená-la, imprimindo as portas necessárias.

    Args:
        k (int): Número de bits.
        vet_s (list): O vetor da permutação.
    """
    n = 1 << k  # 2^k, a quantidade total de valores
    limite = -1
    cont = 0
    listaPortas = []

    # Itera de N-1 para 0, tentando colocar cada valor i na sua posição correta vet_s[i]
    for i in range(n - 1, -1, -1):
        limite += 1
        x = i
        
        # Se o valor na posição 'i' já não for o correto
        if vet_s[i] != x:
            # z contém os bits que precisam ser invertidos para transformar vet_s[i] em x
            z = x ^ vet_s[i]
            
            # Para cada bit que precisa ser mudado, aplica uma porta
            for j in range(k):
                # Verifica se o j-ésimo bit está setado em z
                if (z & (1 << j)) > 0:
                    listaPortas.append(porta(k, vet_s[i], j + 1, vet_s, limite))
                    cont += 1
    
    #print(f"\n{cont} iterações (portas)")

    return listaPortas[::-1]

def cria_portas_sintese_nova(n_bits, A, N):
    saida = calculate_exp_table(n_bits, A, N)

    portas = hipercubo(n_bits, saida)

    return portas

def cria_circuito_sintese_nova(n_bits, A, N, controlado=False):
    portas = cria_portas_sintese_nova(n_bits, A, N)

    q_reg = QuantumRegister(n_bits, "qreg")

    qc = QuantumCircuit(q_reg)
    
    for porta in portas:
        ctrl_state = ""
        if porta:
            for bit in range(len(porta)):

                if porta[bit] == "*":
                    targetidx = bit

                else:
                    ctrl_state = porta[bit] + ctrl_state

            qc.mcx(control_qubits=q_reg[0:targetidx]+q_reg[targetidx+1:], target_qubit=q_reg[targetidx], ctrl_state=ctrl_state)

    return qc.to_gate()
