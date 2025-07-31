import sys
import random
import copy
import time
from math import log, factorial
from sympy.combinatorics.permutations import Permutation, Cycle


def main(argv=None):
    start = time.time()   # in seconds
    f = open('algociclos_3bits.txt', mode='w')   # abre arquivo para imprimir as distâncias
    b = open('algociclos_3bitsb.txt', mode='w')   # abre arquivo para imprimir as distâncias bid.
    
    n = 3
    size = 2**n
    iota = Permutation([], size=2**n)  # permutação Identidade para n bits
    perm_list = set()
    permutacoes = []

 # Pré-processamento - Matriz!   
    matriz = matriz_perm(n)
    for linha in matriz:
        print(linha)    
    print('----------------------------------------------') 

    # Random
##############################################################################################        
##    while len(perm_list) < 1000:
##        temp = list(range(2**n))  # temp = list(range(2**n))
##        random.shuffle(temp)  # random.shuffle(temp)
##        pi = Permutation(temp)
###        print('temp = ', temp, ', pi = ', pi)
##        perm_list.add(tuple(temp)) # `tuple` because `list`s are not hashable.
##        
##    permutacoes = sorted(perm_list)
##    print('len(permutações) = ', len(permutacoes))
##    
##    contador = 0
##
##    for pi in permutacoes:           # para testar um conjunto de permutações    
##        pi = Permutation(pi)
##        sigma = Permutation(inv(n, pi))
##        
##        fi = pi
##        countPorts = 0
##                
####        if contador == 100 or contador == 200 or contador == 300 or contador == 400 or contador == 500 or contador == 700 or contador == 900:
####            print('contador = ', contador)
####        contador += 1
##        
##        nc = 0
##        inicio = 0
##        while nc < (n-1):
##            temp  = fi
##            sinal = 0
##            lim = (combinacao(n-1,nc)*(2**(nc)))    # quantidade de possiveis portas com nc controles
##            for i in range(int(lim)):
##                for j in range(n):
##                    piaux = fi * matriz[inicio+i][j]
##                    if dh_perm_perm(piaux) < dh_perm_perm(temp):
##                        temp = piaux
##                        sinal = 1
##            if sinal == 0:
##                nc += 1
##                inicio += int(lim)
##            else:
##                countPorts += 1
##            fi = temp
##        
##        dist = calcula_dist(fi, countPorts)
##        if dist == 0 and pi != iota:
##            print('Erro!! Não conseguiu resolver ', file=f, flush=True)
##            print('Erro!! Não conseguiu resolver ', pi)
##            break
###        print('Total de Portas = ', dist)
##        print(dist, file=f, flush=True)
##        
##########################################################################################################
    pi = iota + 1
    pi_final = iota    
    sigma = Permutation(inv(n, pi))        
    while pi != pi_final:           # para testar um conjunto de permutações        
        fi = pi
        countPorts = 0
#        print(pi.rank(), ' ====> ', pi)

        if pi.rank() == 100 or pi.rank() == 1000 or pi.rank() == 5000 or pi.rank() == 10000 or pi.rank() == 20000 or pi.rank() == 30000 or pi.rank() == 35000:
            print('pi.rank() = ', pi.rank())
        
        nc = 0
        inicio=0
        while nc < (n-1):
            temp  = fi
            sinal = 0
            lim = (combinacao(n-1,nc)*(2**(nc)))    # quantidade de possiveis portas com nc controles
#            print('nc = ', nc, ' lim = ', lim)
            for i in range(int(lim)):
#                print('i = ', i)
                for j in range(n):
#                    print('j = ', j)
                    piaux = fi * matriz[inicio+i][j]
##                    print('piaux = fi * matriz[',i,'][',j,'] = ', fi, '*', matriz[i][j])
##                    print('temp = ', temp, ' piaux = ', piaux, ' fi = ', fi)                   
##                    print('dh(piaux) = ', dh_perm_perm(piaux),' dh(fi) = ',  dh_perm_perm(temp))
                    if dh_perm_perm(piaux) < dh_perm_perm(temp):
                        temp = piaux
                        sinal = 1
#                        print('sinal = ', sinal, 'temp = ', temp)
            if sinal == 0:
                nc += 1
                inicio +=int(lim)
            else:
                countPorts += 1
            fi = temp
#                print('fi = ', fi,'\n countPorts = ', countPorts)
                
#        fi, countPorts = Not(fi, countPorts)
#        fi, countPorts = CnNot3bits(fi, countPorts)                            
        dist = calcula_dist(fi, countPorts)
        
        if dist == 0 and pi != iota:
            print('Erro!! Não conseguiu resolver ', file=f, flush=True)
            print('Erro!! Não conseguiu resolver ', pi)
            break
#        print('Total de Portas = ', dist)
        print(dist, file=f)
#        pi = pi_final           
###################################################################################################
################################################
        fi = sigma
        countPorts = 0
        
        nc = 0
        inicio = 0
        while nc < (n-1):
            temp  = fi
            sinal = 0
            lim = (combinacao(n-1,nc)*(2**(nc)))    # quantidade de possiveis portas com nc controles
            for i in range(int(lim)):
                for j in range(n):
                    piaux = fi * matriz[inicio+i][j]
                    if dh_perm_perm(piaux) < dh_perm_perm(temp):
                        temp = piaux
                        sinal = 1
            if sinal == 0:
                nc += 1
                inicio += int(lim)
            else:
                countPorts += 1
            fi = temp
        
        dist2 = calcula_dist(fi, countPorts)

        if dist2 < dist:
            dist = dist2

        if dist == 0 and pi != iota:
            print('Erro!! Não conseguiu resolver ', file=b, flush=True)
            print('Erro!! Não conseguiu resolver ', pi)
            break       
        print(dist, file=b)

#        pi = pi_final
              
        pi = pi+1
        sigma = Permutation(inv(n, pi)) 
              
    end = time.time()
    print(end - start)    # in seconds
###################################################################
    
def inv(n, perm):
    inverse = [0]*2**n
    for i, p in enumerate(perm):
        inverse[p] = i
    return inverse

def calcula_dist(pi, countPorts):
    n = int(log(pi.size, 2))
    size = pi.size
    iota = Permutation([], size=2**n)
   # countPorts = 0     # conta o número de portas usadas
    
    while pi != iota:
        atempt = search_2move(pi)
        if atempt != None:
            pi = atempt
            countPorts += 1
#            print('2m -> countPorts = ', countPorts)
#            print('A Permutação', pi, 'é resultado de ação de 2-move.')
            continue

        atemp, aux = search_seq(pi)
        if aux != 0:
            pi = atemp
            countPorts += aux
#            print('seq -> countPorts = ', countPorts)
#            print(aux, 'portas em seq. A Permutação', pi, 'é resultado de ações de portas 0-move e 2-move.')
            continue
        
        atempt = search_0move(pi)
        if atempt != None:
            pi = atempt
            countPorts += 1
#            print('countPorts = ', countPorts)
#            print('A Permutação', pi, 'é resultado de ação de 0-move.')
            continue
        
        atempt, count = Alg_2(pi)
        if atempt != None:
            pi = atempt
            countPorts += count
#            print(count-1, '0-moves and after 1 2-move:', pi)
#            print('Algoritmo 2: ', pi)
#            print('Alg_2 -> countPorts = ', countPorts, '\n')
            continue
       
#        print('Número de portas:', ' ====> ', countPorts)
        print('************************* Nao resolveu ********************', pi, '\n')
        return 0
#        print(pi.rank(), ' ====> ', pi)            # mostra o valor associado à permutação
    return countPorts


def matriz_perm(n):
  seq = [0, 2, 3]  # número de possibilidades para cada linha
  res = [[0 for j in range(n-1)] for i in range(3**(n-1))] # combinações para linhas não-alvo
  n_res = [[0 for j in range(n-1)] for i in range(3**(n-1))] # combinações para todas as linhas.
  pos = [0]*(3**(n-1)) # mudança no n° de controles.
  
  for i in range(3**(n-1)):
    k = i
    for j in range(n-1):
      res[i][j] = seq[k % 3]
      k = k//3
#      k = i//(3**j)
#  print('res = ', res)
  
  posicao = [0]*(n)
  for c in range(1, n): # c = n° de controles
    d = (combinacao(n-1,c-1)*(2**(c-1)))  
    posicao[c] = (posicao[c-1] + int(d)) # posição de mudança no n° de controles    
#  print('posição = ', posicao)
  
  ctrl = [0]*3**(n-1)
  for i in range(3**(n-1)): # Nova posição de acordo com o n° de controles  
#    print('res[',i,'] = ', res[i])
    c = controles(res[i], n-1)
    ctrl[i] = c
    pos[i] = posicao[c]
#    print('pos[',i,'] = ', posicao[c])
    posicao[c] += 1
    
#  print('pos = ', pos)       
  for i in range(3**(n-1)):
#    print('i = ', i, ' pos[',i,'] = ', pos[i])    
    n_res[pos[i]] = res[i]
#    print('n_res[', pos[i], '] = ', n_res[pos[i]], ' = ', res[i])
#  print('n_res = ', n_res)
  
  # cria a matriz com zeros
  linha = [0]*n
  matriz = []
  for i in range(3**(n-1)):
      matriz.append([0]*n)
#  print('----------------------------------------------')
  for i in range(3**(n-1)-1, 3**(n-1)-2**(n-1)-1, -1): # totalmente controlada (n-1 controles)
      for k in range(0, n, 1):
          seq_temp = n_res[i][:]
          seq_temp.insert(k,1)
#          print(seq_temp)
          matriz[i][k] = seq2perm(seq_temp, n)
##          print('matriz[',i,'][',k,'] = ', matriz[i][k])          
##  print('----------------------------------------------')          
  for i in range(3**(n-1)-2**(n-1)-1, -1,-1): # n-2 controles, n-3 controles, ..., 0 controle.
      pos_m = 0
      pos_zero = -1
#      print('i = ', i, ' pos_m = ', pos_m, ' pos_zero = ', pos_zero)
      for j in range(n-1):
#          print('j = ', j, ' n_res[',i,'][',j,'] = ', n_res[i][j])
          pos_m += ((n_res[i][j])+1)//2*(3**j)
#          print('pos_m = ', pos_m)          
          if n_res[i][j] == 0:
              pos_zero = j
#              print('pos_zero = ', pos_zero)
      pos_p = pos_m + 3**pos_zero
      pos_q = pos_m + 2*3**pos_zero
#      print('pos_p = ', pos_p, ' pos_q = ', pos_q)
      p = pos[pos_p]
      q = pos[pos_q]
#      print('p = ', p, ' q = ', q)
      for j in range(n):
#          print('matriz[',p,'][',j,'] = ', matriz[p][j], ', matriz[',q,'][',j,'] = ', matriz[q][j])
          matriz[i][j] = matriz[p][j] * matriz[q][j]
##          print('matriz[',i,'][',j,'] = ', matriz[i][j])          
##  print('----------------------------------------------')
          
##  for linha in matriz:
##      print(linha)      
  return matriz         


# Procura 1o um 2-move T que junta ciclos (P(pi*T)>P(pi)), caso não exista, procura um 2-move que separa ciclos, senão retorna None
def search_2move(pi):
#    print('Entrou em 2-move')
    iota = Permutation([], size=pi.size)
    T_temp = iota
    n = int(log(pi.size, 2))
    dmin = pi.size
    pi_return = None
    for cycle in pi.cyclic_form:
        for element in cycle:
            for i in range(len(cycle)):
                if element == cycle[i]:
                    d_atual= dh_int_int(cycle[i-1], cycle[i])
            for neighbor in neighbors(element, n):
                piaux = pi*swap(element, neighbor)
                if dh_perm_perm(piaux) < dh_perm_perm(pi): # verifica se há 2-move
                    if pi_return == None:   # verifica se é o 1o 2-move encontrado
                        pi_return = piaux
                    if P(piaux) > P(pi) and d_atual < dmin: # verifica se o 2-move junta ciclos e se a d.h. entre os vizinhos tratados é mínima
                        dmin = d_atual
                        pi_return = piaux
#                    print('Porta trocando ', element, ' com ', neighbor, ' eh 2-move')
                    T_temp = swap(element, neighbor)
    return pi_return


# Procura um 0-move que junta ciclos
def search_0move(pi):
#    print('Entrou em 0-move')
    n = int(log(pi.size,2))
    dmin = pi.size
    pi_return = None
    for cycle in pi.cyclic_form:
        for element in cycle:
            for i in range(len(cycle)):
                if element == cycle[i]:
                    d_atual = dh_int_int(cycle[i-1], cycle[i])
            for neighbor in neighbors(element, n):
                piaux = pi*swap(element, neighbor)
                if dh_perm_perm(piaux) == dh_perm_perm(pi) and P(piaux) < P(pi):
                    if d_atual < dmin:
                        dmin = d_atual
                        pi_return = piaux
##                    print('Porta  trocando ', element, ' com ', neighbor,\
##                        ' eh 0-move')
    return pi_return

    # Verifica se, num ciclo, há uma sequencia de 0-moves que termine com um 2-move.
    # Em caso afirmativo, aplica tal sequencia.
def search_seq(pi):
#    print('Entrou em seq')
    for cycle in pi.cyclic_form:
        countPorts = 0        # conta o número de portas aplicadas
        flagServe = 0
        if len(cycle) == 2:   # se houvesse 2-move, ele foi aplicado antes
            break
        beginSeq = len(cycle)       # marca 1a dist > 1
        endSeq = len(cycle)         # marca 2a dist > 1
#p#        print(cycle)
        for i in range(len(cycle)):
            if dh_int_int(cycle[i-1], cycle[i]) != 1:
                if beginSeq == len(cycle):    # 1a vez dist >1 que aparece no ciclo
                    beginSeq = i-1
                elif endSeq == len(cycle):    # 2a vez dist >1 que aparece no ciclo
                    endSeq = i-1
#p#                print('!!',beginSeq,endSeq)
                if endSeq < len(cycle):           # há pelo menos 2 com dist > 1
                    if dh_int_int(cycle[beginSeq], cycle[endSeq]) == 1:       # para garantir que o último movimento seja 2-move
                        piaux = pi
                        for j in range(beginSeq+1, endSeq):
                            piaux = piaux*swap(cycle[j], cycle[j+1])            # não necessariamente 0-move
                            countPorts += 1 
##                            print('         2a:(',countPorts,'):',piaux);
##                        print(cycle, beginSeq, endSeq)
                        return piaux, countPorts     # não faz um possível movimento
                    else:
                        beginSeq = endSeq       # recomeça a procurar
                        endSeq = len(cycle)+1    # não usar endSeq = len(cycle) para reinicializá-lo
#p#                        print('         continua tentando...')
        if beginSeq == len(cycle):        # se todas as distâncias entre vizinhos são 1, desmonta todo ciclo 
#p#            print('Desmonta ciclo ',cycle)
            piaux = pi
            for i in range(len(cycle)-1):
                piaux = piaux*swap(cycle[i-1], cycle[i])
                countPorts += 1
#                print('         0:(',countPorts,'):',piaux);
            return piaux, countPorts
        elif endSeq == len(cycle):      # se houver apenas uma distância diferente de 1, desmonta todo ciclo
#p#            print('Desmonta ciclo ',cycle)
            piaux = pi
            for i in range(beginSeq+1, len(cycle)-1):
                piaux = piaux*swap(cycle[i], cycle[i+1])
                countPorts += 1
#                print('         1:(',countPorts,'):',piaux);
            for i in range(beginSeq+1):
                piaux = piaux*swap(cycle[i-1], cycle[i])
                countPorts += 1
#                print('         1:(',countPorts,'):',piaux);
#            print('Portas em seq = ', countPorts)
            return piaux, countPorts
    return None, 0


# função 2moveD baseada na 2move original
def search_2moveD(pi):
    iota = Permutation([], size = pi.size)
    T_temp = iota
    n = int(log(pi.size,2))
    dmin = pi.size
    pi_return = None
    for cycle in pi.cyclic_form:
        for element in cycle:
            for i in range(len(cycle)):
                if element == cycle[i]:
                    d_atual = dh_int_int(cycle[i-1], cycle[i])
            for neighbor in neighbors(element, n):
                piaux = pi * swap(element, neighbor)
                if dh_perm_perm(piaux) < dh_perm_perm(pi) and (neighbor in cycle): # verifica se há 2-moveD
                    pi_return = piaux
                    return pi_return
##                    if P(piaux) > P(pi) and d_atual < dmin: # verifica se o 2-move junta ciclos e se a d.h. entre os vizinhos tratados é mínima
##                        dmin = d_atual
##                        pi_return = piaux
##                    T_temp = swap(element, neighbor)
    return pi_return


# Procura 1o um 2-move T que junta ciclos (P(pi*T)>P(pi)), caso não exista, procura um 2-move que separa ciclos, senão retorna None
# Sequência útil com 2-move
def Alg_2(pi):
#    print('tentou Algoritmo 2')
#    print('pi: ', pi)
    size = pi.size
    piaux = []
    count = 0
    flag = 0              
    j = size - 1
    while j > 0 and flag == 0:
#        print('j: ', j, 'pi(j): ', pi(j))
        while j == pi(j):
            j -= 1
#            print('j: ', j, 'pi(j): ', pi(j))
        piaux,count,flag = replace(pi, j, pi(j), count)
#        print('flag: ', flag)
        pi = piaux
        j -= 1
#        print('j: ', j, 'pi: ', pi)
    return piaux,count


def CnNot3bits(pi, countPorts):
    a = [-1]*3
    pi_return = None
    temp = [x for x in range(8)]

    for j0 in range(2, -1, -1):
        for j1 in range(2, -1, -1):
            for j2 in range(3):
                a[j2] = 3
                a[(j2+1)%3] = j0
                a[(j2+2)%3] = j1
                for i in range(pi.size): #aplica a porta em todos os elementos de pi
                    temp[i] = CnNot(pi(i),a)
                pi_temp = Permutation(temp)
                if dh_perm_perm(pi_temp) < dh_perm_perm(pi):
                    countPorts = countPorts + 1
                    pi = pi_temp #atualiza pi
    pi_return = pi
    return pi_return, countPorts


def CnNot(numero, controle):
    atua = 1
    alvo = 0
    for h in range(len(controle)):
        teste = (numero)&(1<<h)
        teste = teste >> h
        if controle[h] == 0 or controle[h] == 1:
            if controle[h] != teste:
                atua = 0
        if controle[h] == 3:
            alvo = h
    if atua:
        numero = (numero)^(1<<alvo)
    return numero


def Not(pi, countPorts):
    n = int(log(pi.size,2))
    size = pi.size
    dif = [] 
    for i in range(size):
        dif.append(pi.array_form[i]^i)
    ndb = [0] * n
    for j in range(n):
        mask = 1 << j
        for i in range(size):
            if dif[i] & mask:
                ndb[j] += 1
         # Porta NOT    
    temp = copy.copy(pi.array_form)
    for i in range(n):
        mask = 1 << i
        if ndb[i] > (size/2):
            for j in range(size):
                temp[j] = temp[j] ^ mask
            countPorts += 1       
    pi = Permutation(temp)
    pi_return = pi
    return pi_return, countPorts


# Faz a troca entre i e i_line até a distância entre i e j chegar a 1, daí aplica a Porta e retorna p/ Alg_2  
def replace(pi, j, i, count):
    n = int(log(pi.size,2))
    indice = 0
    pi_return = []
    i_line = 0
#    i_old = 0 
    while dh_int_int(i, j)!=1:            # Enquanto não puder colocar j na sua posição, faz (i <- i')
        x = i ^ j
        k = 0
        while k < n:      # signal será igual a 1 quando o bit i_k for diferente de j_k
            zeroum = (x>>k) & 1
#            print('k: ', k, 'zeroum: ', zeroum)
            if zeroum == 1:
                indice = k
#                print('indice: ', indice)
                break
            k += 1
        i_line = i ^ (2**(indice))
        #    print('i: ', i, 'i_line: ', i_line)
        piaux = pi*swap(i,i_line)
        count += 1
#        print('A Porta ', 'T(', i,',', i_line,') eh aplicada quando dh_int_int(i,j)!=1')
#        print('count: ', count, ', piaux: ', piaux)
#        print('Se é !=, count: ', count)
#        i_old = i
        i = i_line
        pi = piaux     
#    print('Temos que dh_int_int(',i,',',j,'): ',dh_int_int(i, j))
    pi_return = pi*swap(i, j)
    count += 1
    if dh_perm_perm(pi_return) < dh_perm_perm(pi):
        dm = 1
    else:
        dm = 0          
#    print('A Porta ', 'T(', i,',', j,') eh aplicada em replace pois dh_int_int(i,j)==1')
#    print('Se é ==, count: ', count)
#    print('count: ', count, ', pi_return: ', pi_return, 'dm: ', dm)
    return pi_return,count,dm


def seq2perm(seq, n):
    a = b = 0
    p = Permutation([], size=2**n)
    for i in range(n):
        if seq[i] == 1:
            a += 0*2**i
            b += 1*2**i
        elif seq[i] == 2:
            a += 0*2**i
            b += 0*2**i
        elif seq[i] == 3:
            a += 1*2**i
            b += 1*2**i
    p = Permutation(a, b)        
    return p


def controles(x, n): # função retorna o número de controles.
  c = 0
  for i in range(n):
    if x[i] :   # verifica se é diferente de zero
      c += 1
  return c


def fatorial(n, limite = 1):
	if n == 0 or n == 1:
		return 1 #por definição 0! ou 1! = 1
	if limite < 1 or limite > n:
		return -1 #representando valor incorreto
	else :
		fatArr = range(limite, n+1)
		resultado = 1
		for i in fatArr:
			resultado = resultado * i
		return resultado


def combinacao(n, p):
	if p > n:
		return -1
	a = b = limite = 1
	np = n - p
	if np < p:
		limite = np+1
		b = p
	else:
		limite = p+1
		b = np
	a = fatorial(n, limite)
	b = fatorial(b)
	return a/b


def P(perm):
    aux = 0
    for cycle in perm.cyclic_form:
        aux += S(cycle)/len(cycle)
    return aux


def S(cycle):
    size = len(cycle)
    aux = 0
    for i in range(size):
        aux += dh_int_int(cycle[i-1], cycle[i])
    return aux


def neighbors(a, size):
    aux = []
    for i in range(size):
        aux.append(a ^ (1 << i))
    return aux


def dh_perm_perm(p, q=None):
    
    if q is None:
        q = Permutation([], size=p.size)
    elif p.size != q.size:
        raise ValueError('permutations must be of same sizes')

    dist = 0
    for i in range(p.size):
        pi = p.array_form[i]
        qi = q.array_form[i]
        dist += dh_int_int(pi, qi)

    return dist


def dh_perm_int(p, a):
    return dh_int_int(p.array_form[a], a)


def dh_int_int(a, b, bits = 64):
    x = a ^ b
    return sum((x >> i & 1) for i in range(bits))


# aplica a transposição na permutação se a dist. Hamming for 1
def swap(i, j):
    if dh_int_int(i, j) == 1:
        return Permutation(i, j)
    else:
        raise ValueError('Invalid Transposition!!')
        return 0


def unicyclic(n, index = 0):
    sigma = Permutation([], size=(2**n)-1)  # permutação Identidade para n-1 bits
    sigma = sigma + index
    return Permutation(list(Permutation([sigma.list(2**n)])))


if __name__ == "__main__":
    sys.exit(main())

