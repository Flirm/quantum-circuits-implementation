from typing import List
import re
import copy
import time
from pathlib import Path
import numpy as np
from itertools import product
from math import log2
from enum import Enum

"""
Arquivo para realizacao da sintese do circuito feito pelo Raphael Bernadino
Implementacao original: https://github.com/raphaelbernardino/rblk
"""


class Alvo:
    def __init__(self, linha, mapa=None):
        self.linha_original = int(linha)

        if mapa is None:
            self.linha = int(linha)
        else:
            if linha >= len(mapa):
                self.linha = linha
            else:
                self.linha = int(mapa[linha])

        if self.linha < 0:
            raise Exception('Alvo inválido! Linha negativa.')

    def modifica_linha(self, modificacao: int):
        """
        Modifica a linha atual. Para aumentar a linha informe um valor positivo, e para diminuir, um valor negativo.

        modificacao: int
        """
        self.linha = self.linha + modificacao

    def remapeia(self, mapa):
        self.linha = mapa[self.linha]

    def __repr__(self):
        return f'b{self.linha}'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.linha != other.linha:
            return False

        return True

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise Exception('Não é possível comparar Alvo com outro tipo.')

        return self.linha < other.linha

    def __hash__(self):
        return id(self.linha) * hash(self.linha + 1)



class States(Enum):
    alvo = 'av'
    ctrl_ausente = None
    ctrl_positivo = True
    ctrl_negativo = False

    def __eq__(self, other):
        other_value = other

        if type(other_value) is self:
            other_value = other_value.value

        return other_value == self.value

    def __repr__(self):
        if self.value == self.ctrl_positivo:
            return 'Positivo'

        if self.value == self.ctrl_negativo:
            return 'Negativo'

        if self.value == self.ctrl_ausente:
            return 'Ausente'

        # return str(self.value)
        return 'Alvo'

    def __str__(self):
        return self.__repr__()
    

class Controle:
    def __init__(self, linha, sinal, mapa=None):
        self.linha_original = int(linha)

        if mapa is None:
            self.linha = int(linha)
        else:
            if linha >= len(mapa):
                self.linha = linha
            else:
                self.linha = int(mapa[linha])

        if isinstance(sinal, bool):
            self.sinal = sinal

        elif isinstance(sinal, States):
            self.sinal = bool(sinal.value)

        else:
            raise Exception('Sinal inválido! Não é booleano.')

        if self.linha < 0:
            raise Exception('Controle inválido! Linha negativa.')

    def modifica_linha(self, modificacao: int):
        """
        Modifica a linha atual. Para aumentar a linha informe um valor positivo, e para diminuir, um valor negativo.

        modificacao: int
        """
        self.linha = self.linha + modificacao

    def remapeia(self, mapa):
        self.linha = mapa[self.linha]

    def eh_sinal_positivo(self):
        return self.sinal == States.ctrl_positivo

    def eh_sinal_negativo(self):
        return self.sinal == States.ctrl_negativo

    def inverte_sinal(self):
        self.sinal = not self.sinal

    def possui_sinal_inverso(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.linha != other.linha:
            return False

        if self.sinal == other.sinal:
            return False

        return True

    def __repr__(self):
        s = "" if self.sinal else "'"
        return f'b{self.linha}{s}'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.sinal != other.sinal:
            return False

        if self.linha != other.linha:
            return False

        return True

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise Exception('Não é possível comparar Controle com outro tipo.')

        return self.linha < other.linha

    def __hash__(self):
        return id(self.sinal) * hash(self.linha + 1)


class Toffoli:
    def __init__(self, alvos: List[Alvo], controles: List[Controle], mapa=None):
        self.tamanho_bits = 1 + len(controles)

        self.mapeamento = mapa
        if mapa is None:
            # k = [(i, i) for i in range(self.tamanho_bits)]

            # busca a maior linha de alvo
            maior_linha_alvo = 0
            if isinstance(alvos, list):
                maior_linha_alvo = alvos[0].linha
            elif isinstance(alvos, Alvo):
                maior_linha_alvo = alvos.linha
            else:
                raise Exception(f'Alvo não possui um tipo identificavel. (alvos: {type(alvos)})')

            # busca a maior linha de controle
            maior_linha_controle = 0
            if len(controles) > 0:
                maior_linha_controle = max([ctrl.linha for ctrl in controles])

            # identifica a maior linha entre controles e alvos
            maior_linha = max(maior_linha_alvo, maior_linha_controle)
            # print(f'Maior linha:: {maior_linha_alvo} :: {maior_linha_controle} ==> {maior_linha}')

            # gera o mapeamento a partir da maior linha
            k = [(i, i) for i in range(maior_linha + 1)]
            self.mapeamento = dict(k)

        self.alvos = self.__inicializa_alvos(alvos)
        self.controles = self.__inicializa_controles(controles)

    # def mapeia(self, mapa):
    #     # realiza mapeamento do alvo
    #     self.alvos.mapeia(mapa)
    #
    #     # realiza mapeamento dos controles
    #     for controle in self.controles:
    #         controle.mapeia(mapa)

    def modifica_linhas(self, mapeamento: dict):
        """
        Modifica a linha atual através de mapeamento.

        @param mapeamento: Um dicionário contendo o mapeamento a ser realizado.
        """
        linha_alvo = self.alvos.linha
        nova_linha_alvo = mapeamento[linha_alvo]

        diferenca_linha = linha_alvo - nova_linha_alvo
        self.alvos.modifica_linha(diferenca_linha)

        for ctrl in self.controles:
            linha_ctrl = ctrl.linha
            nova_linha_ctrl = mapeamento[linha_ctrl]

            diferenca_linha = linha_ctrl - nova_linha_ctrl
            ctrl.modifica_linha(diferenca_linha)

    def __inicializa_alvos(self, alvos):
        alvo = list()

        if isinstance(alvos, Alvo):
            um_alvo = copy.deepcopy(alvos)
            um_alvo.linha_original = alvos.linha
            um_alvo.linha = self.mapeamento[alvos.linha]
            alvo.append(um_alvo)

        if isinstance(alvos, list):
            # alvo = [copy.deepcopy(a) for a in alvos]
            for a in alvos:
                um_alvo = copy.deepcopy(a)
                um_alvo.linha_original = a.linha
                # print(f'Mapeamento: {self.mapeamento}')
                # print(f'Alvos: {alvos}')
                # print(f'Linha: {a.linha}')
                # print(f'um_alvo: {um_alvo} :: {um_alvo.linha} :: {um_alvo.linha_original}')
                um_alvo.linha = self.mapeamento[a.linha]
                alvo.append(um_alvo)

        if isinstance(alvos, int):
            um_alvo = Alvo(alvos, self.mapeamento)
            alvo.append(um_alvo)

        if len(alvo) != 1:
            raise Exception('Alvos inválidos! É necessário apenas um alvo.')

        return alvo[0]

    def __inicializa_controles(self, ctrls: List[Controle]):
        controles = list()

        for ctrl in ctrls:
            um_controle = copy.deepcopy(ctrl)
            # print(f'Mapeamento: {self.mapeamento}')
            # print(f'Linha Original: {ctrl.linha} :: {um_controle.linha_original} :: {um_controle.linha}')
            um_controle.linha_original = ctrl.linha
            um_controle.linha = self.mapeamento[ctrl.linha]
            controles.append(um_controle)

        return controles

    def remapeia(self, mapa):
        self.alvos.remapeia(mapa)

        for ctrl in self.controles:
            ctrl.remapeia(mapa)

    def adiciona_controles(self, controles):
        # linhas_usadas = self.obtem_linhas_de_controle_usadas()
        linhas_usadas = self.obtem_linhas_usadas()
        controles_antigos = copy.deepcopy(self.controles)

        for ctrl in controles:
            if ctrl.linha in linhas_usadas:
                self.controles = controles_antigos
                raise Exception('Linha {ctrl.linha} já está ocupada')

            um_controle = copy.deepcopy(ctrl)
            self.controles.append(um_controle)
            self.tamanho_bits = len(self.obtem_linhas_usadas())

    def remove_controle(self, ctrl):
        if ctrl in self.controles:
            self.controles.remove(ctrl)
            self.tamanho_bits = len(self.obtem_linhas_usadas())

    def remove_controles(self, controles):
        for ctrl in controles:
            self.remove_controle(ctrl)

    def obtem_alvos(self):
        return [self.alvos]

    def obtem_copia(self):
        return copy.deepcopy(self)

    def calcula_custo_cnot(self):
        """
        Calcula o custo de CNOTs a partir da quantidade de controles usados.
        Usando como referência o artigo: https://iopscience.iop.org/article/10.1088/2058-9565/acaf9d/meta
        Automatic generation of Grover quantum oracles for arbitrary data structures. Raphael Seidel et al. (2023).

        @return: O custo de CNOTs da porta.
        """
        n = len(self.controles)
        return 2 * n ** 2 - 2 * n + 1

    def calcula_custo_quantico(self):
        """
            https://reversiblebenchmarks.github.io/definitions.html
            https://physics.stackexchange.com/a/236054
            Rahman, Md Zamilur, and Jacqueline E. Rice. "Templates for positive and negative control Toffoli networks."
            International Conference on Reversible Computation. Springer, Cham, 2014.
                https://opus.uleth.ca/bitstream/handle/10133/3727/RAHMAN_MD_ZAMILUR_MSC_2015.pdf
            
            -- POSITIVE --
            n = 1 ==> QC =   1
            n = 2 ==> QC =   1
            n = 3 ==> QC =   5
            n = 4 ==> QC =  13
            n = 5 ==> QC =  29
            n = 6 ==> QC =  61
            n = 7 ==> QC = 125
            n = 8 ==> QC = 253
            n = 9 ==> QC = 509
            n > 9 ==> QC = 2**n - 3
            
            -- NEGATIVE -- 
            n = 1 ==> QC =   1
            n = 2 ==> QC =   1+2
            n = 3 ==> QC =   5+1    (see below)
            n = 4 ==> QC =  13+2
            n = 5 ==> QC =  29+2
            n = 6 ==> QC =  61+2
            n = 7 ==> QC = 125+2
            n = 8 ==> QC = 253+2
            n = 9 ==> QC = 509+2
            n > 9 ==> QC = 2**n - 1
            
            -- observation:: n = 3
            == Rahman, Md Zamilur, and Jacqueline E. Rice (2.8.3. Quantum Cost)
            The cost of T (a, b, c) T (a, b) (Peres gate) or T (a, b) T (a, b, c) 
            (inverse of Peres gate) is set to be 4 instead of 5 + 1 = 6, as the 
            quantum implementation of each of these patterns was found with cost 4.
        """
        custo_total = 0
        n = self.tamanho_bits

        if n == 1:
            # not
            custo_total += 1

        elif n == 3:
            # ccnot
            custo_total += 5

            if self.todos_controles_negativos():
                custo_total += 1

        else:
            # toffoli generalizada
            custo_total = 2 ** n - 3

            if self.todos_controles_negativos():
                custo_total += 2

        return custo_total

    def todos_controles_negativos(self):
        for ctrl in self.controles:
            # se o sinal é positivo, retorna False
            if ctrl.eh_sinal_positivo():
                return False

        # se todos os sinais são negativos, retorna True
        return True

    def eh_porta_not(self):
        return len(self.controles) == 0

    def eh_adjacente(self, other):
        if self.obtem_alvos() != other.obtem_alvos():
            return False

        diff = self.diferenca_entre_controles(other)
        diffs = len(diff)

        # pode diferir apenas em uma linha; se não houver ctrls diff, não é
        if diffs == 0:
            return False

        # se  houver apenas um controle diff, é adjacente
        if diffs == 1:
            return True

        # se houver exatamente dois controles, verifique as linhas
        if diffs == 2:
            gc = diff[0]
            hc = diff[1]

            return gc.linha == hc.linha

        # se houver mais de 2 ctrls diff. não pode ser adjacente
        return False

    def diferenca_entre_controles(self, other):
        s1 = set(self.controles)
        s2 = set(other.controles)
        diff = s1.symmetric_difference(s2)
        return sorted(diff)

    def obtem_linhas_de_alvo_usadas(self):
        linhas_usadas = set()
        linhas_usadas.add(self.alvos.linha)
        return linhas_usadas

    def obtem_linhas_de_controle_usadas(self):
        linhas_usadas = set()

        for ctrl in self.controles:
            linha = ctrl.linha
            linhas_usadas.add(linha)

        return linhas_usadas

    def obtem_linhas_usadas(self):
        linhas_de_alvo = self.obtem_linhas_de_alvo_usadas()
        linhas_de_controle = self.obtem_linhas_de_controle_usadas()

        linhas_usadas = linhas_de_alvo.union(linhas_de_controle)

        return linhas_usadas

    def inverte_controle_nas_linhas(self, linhas):
        for linha in linhas:
            for ctrl in self.controles:
                if linha == ctrl.linha:
                    ctrl.inverte_sinal()

    def roda_porta_permutacao(self, elementos):
        for i in range(len(elementos)):
            elem = elementos[i]
            # print('ELEM_ANTES -->', elem)

            if self.__deve_aplicar(elem):
                elementos[i] = self.__aplica(elem)

    def roda_porta_tabela_verdade(self, tabela):
        # print('T', tabela)

        for linha_tabela in tabela:
            alvo = self.alvos

            # print('L1', linha_tabela)

            if self.__deve_aplicar(linha_tabela):
                # print('aplicou')
                linha_tabela[alvo.linha] = int(not linha_tabela[alvo.linha])
                # print('L2', linha_tabela)

    def __deve_aplicar(self, elementos):
        for ctrl in self.controles:
            linha = ctrl.linha
            linha_mapeada = self.mapeamento[linha]
            valor = int(elementos[linha_mapeada])

            if ctrl.eh_sinal_positivo() and valor == 0:
                return False

            if ctrl.eh_sinal_negativo() and valor == 1:
                return False

        return True

    def __aplica(self, e):
        el = list(e)
        # print('\t\tVetor Elementos', el)

        linha_alvo = self.alvos.linha
        # print('\t\tLinha Alvo', linha_alvo)

        linha_alvo_mapeada = self.mapeamento[linha_alvo]
        # print('\t\tMapeamento', self.mapeamento)
        # print('\t\tLinha Alvo Mapeada', linha_alvo_mapeada)

        if el[linha_alvo_mapeada] == '0':
            el[linha_alvo_mapeada] = '1'
        elif el[linha_alvo_mapeada] == '1':
            el[linha_alvo_mapeada] = '0'
        else:
            raise Exception('Algum erro ocorreu!')

        resultado = ''.join(el)
        # print('ELEM_DEPOIS-->', resultado)

        return resultado

    def __repr__(self):
        s = f'T{self.tamanho_bits} '

        for ctrl in sorted(self.controles):
            s += f'{ctrl},'

        s += f'{self.alvos}'

        return s

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.obtem_alvos() != other.obtem_alvos():
            return False

        if len(self.controles) != len(other.controles):
            return False

        if self.controles != other.controles:
            return False

        return True

    def __hash__(self):
        return id(self.alvos) * hash(self.controles) * self.tamanho_bits

    def __len__(self):
        return self.tamanho_bits
    

def gera_porta_circuito(expressao, alvo, prefixo='b', valor_inicial=0):
    partes = expressao.split('&')
    partes = [parte.strip().replace(' ', '') for parte in partes]

    alvos = list()

    if type(alvo) is int:
        alvos = Alvo(alvo)
    else:
        for a in alvo:
            um_alvo = Alvo(a)
            alvos.append(um_alvo)


    # constroi os controles
    controles = list()

    for parte in partes:
        ctrl_linha_str = parte.replace(prefixo, '')
        ctrl_sinal = True

        if parte.startswith('~'):
            ctrl_linha_str = parte[1 + len(prefixo):]
            ctrl_sinal = False

        if ctrl_linha_str != '':
            ctrl_linha = int(ctrl_linha_str)
            ctrl = Controle(ctrl_linha, ctrl_sinal)
            controles.append(ctrl)


    porta = Toffoli(alvos, controles)
    return porta


def gera_tabela_verdade(qtd_bits, ancillas=0):
    for linha in product([0, 1], repeat=qtd_bits):
        temp = list(linha)
        temp += [0] * ancillas
        yield temp


def gera_permutacao(qtd_bits):
    n = 2 ** qtd_bits
    estado = list()
    # estado = np.empty(n, dtype='object')

    for i in range(n):
        k = bin(i)[2:].zfill(qtd_bits)
        estado.append(k)
        # estado[i] = bin(i)[2:].zfill(qtd_bits)

    return estado


def inverte_elementos(elementos):
    for i in range(len(elementos)):
        elementos[i] = elementos[i][::-1]


class Circuito:
    def __init__(self, portas=None, qtd_vars=0, ancillas=0, mapa=None):
        """
            Recebe uma lista de portas e quantidade de variaveis.
        :param portas: Uma lista de Portas do tipo Fredkin ou Toffoli.
        :param qtd_vars: Uma quantidade inteira que representa a quantidade de variaveis.
        """
        self.bits_extras = ancillas
        self.tamanho_circuito = qtd_vars

        self.portas = portas
        if self.portas is None:
            self.portas = list()

        self.mapeamento = mapa
        if self.mapeamento is None:
            mapa = [(i, i) for i in range(self.tamanho_circuito)]
            self.mapeamento = dict(mapa)

        if self.tamanho_circuito is None:
            self.tamanho_circuito = self.__obtem_quantidade_de_variaveis()

        self.portas = self.__adiciona_portas(portas)

        ### apesar de achar que deve ser um atributo, demanda muito tempo gerar a tabela vdd a cada inicializacao
        # self.tabela_verdade = self.obtem_tabela_verdade()
        self.gc = self.custo_porta()
        self.qc = self.custo_quantico()

    def __adiciona_portas(self, info):
        if info is None:
            info = list()

        if isinstance(info, Circuito):
            info = info.portas

        if isinstance(info, tuple):
            info = list(info)

        if isinstance(info, list):
            portas = list()

            for p in info:
                ptemp = copy.deepcopy(p)
                ptemp.mapeamento = self.mapeamento
                portas.append(ptemp)

            return portas

        raise Exception('Circuito:: Operação não suportada!')

    def __obtem_quantidade_de_variaveis(self):
        linhas_usadas = self.obtem_linhas_usadas()
        return len(linhas_usadas)

    def obtem_mapeamentos(self):
        mapa = f'Mapeamento do Circuito: {self.mapeamento}'

        mapa += f'\nMapeamento das portas:'
        for porta in self.portas:
            mapa += f'\n\t{porta} ==> {porta.mapeamento}'

        return mapa

    def obtem_quantidade_de_bits(self):
        return self.tamanho_circuito + self.bits_extras

    def atualiza_informacoes(self):
        """
        Atualiza informações sobre o circuito.

        @return:
        """
        # self.tamanho_circuito = self.__obtem_quantidade_de_variaveis()
        self.tamanho_circuito = 1 + max(self.obtem_linhas_usadas(), default=0)
        self.gc = self.custo_porta()
        self.qc = self.custo_quantico()

    def obtem_copia(self):
        return copy.deepcopy(self)

    def reduz_linhas(self):
        mapeamento = dict()
        ini_vars = self.tamanho_circuito
        ini_ancs = self.bits_extras

        linhas = self.obtem_linhas_usadas()
        linhas = list(linhas)
        # logger.debug(f'Linhas: {linhas}')

        for i in range(0, ini_vars):
            if i not in linhas:
                self.tamanho_circuito -= 1
                continue

            mapeamento[i] = linhas.index(i)

        for i in range(ini_vars, ini_vars + ini_ancs):
            if i not in linhas:
                self.bits_extras -= 1
                continue

            mapeamento[i] = linhas.index(i)

        # logger.debug(f'MAP: {mapeamento}')

        for porta in self.portas:
            porta.modifica_linhas(mapeamento)

    def obtem_linhas_de_alvo_usadas(self):
        linhas_usadas = set()

        for porta in self.portas:
            linhas = porta.obtem_linhas_de_alvo_usadas()
            linhas_usadas = linhas_usadas.union(linhas)

        return linhas_usadas

    def obtem_linhas_de_controle_usadas(self):
        linhas_usadas = set()

        for porta in self.portas:
            linhas = porta.obtem_linhas_de_controle_usadas()
            linhas_usadas = linhas_usadas.union(linhas)

        return linhas_usadas

    def obtem_linhas_usadas(self):
        linhas_de_alvo = self.obtem_linhas_de_alvo_usadas()
        linhas_de_controle = self.obtem_linhas_de_controle_usadas()

        linhas_usadas = linhas_de_alvo.union(linhas_de_controle)
        return linhas_usadas

    def apaga_porta_por_indice(self, indice):
        del self.portas[indice]
        self.atualiza_informacoes()

    # def remove_porta(self, porta):
    #     self.portas.remove(porta)
    #     self.__atualiza_informacoes()

    def insere_porta_por_indice(self, indice, porta):
        self.portas.insert(indice, porta)
        self.atualiza_informacoes()

    # def adiciona_porta(self, porta):
    #    uma_porta = copy.deepcopy(porta)
    #    self.portas.append(uma_porta)
    #    self.__atualiza_informacoes()

    def custo_porta(self):
        return len(self.portas)

    def custo_quantico(self):
        custo_total = 0

        for porta in self.portas:
            custo_total += porta.calcula_custo_quantico()

        return custo_total

    def custo_cnot(self):
        custo_total = 0

        for porta in self.portas:
            # logger.debug(f'Porta: {porta}')
            custo = porta.calcula_custo_cnot()
            # logger.debug(f'Custo: {custo}')
            custo_total += custo
            # logger.debug(f'Total: {custo_total}')

        return custo_total

    def calcula_tamanho(self):
        linhas_usadas = self.obtem_linhas_usadas()
        return max(linhas_usadas)

    def obtem_permutacao(self, qtd_bits=None):
        if qtd_bits is None:
            qtd_bits = self.obtem_quantidade_de_bits()

        elementos = gera_permutacao(qtd_bits)
        # logger.debug(f'Permutacao Inicial: {elementos}')
        # logger.debug(f'Mapeamento: {self.mapeamento}')

        inverte_elementos(elementos)
        for porta in self.portas:
            # logger.debug(f'Aplicando {porta}')
            porta.roda_porta_permutacao(elementos)
            # logger.debug(f'Aplicado {elementos}')
        inverte_elementos(elementos)

        return tuple(elementos)

    def obtem_tabela_verdade(self, n=None, ancillas=None):
        if n is None:
            n = self.tamanho_circuito

        if ancillas is None:
            ancillas = self.bits_extras

        tab_vdd = gera_tabela_verdade(n, ancillas=ancillas)
        # tabela_verdade = list(tab_vdd)
        tabela_verdade = np.fromiter(tab_vdd, dtype=np.dtype((np.uint8, n)), count=2**n)
        # tabela_verdade = np.zeros(shape=(2**n, n), dtype=np.uint8)
        # for i, k in enumerate(tab_vdd):
        #     tabela_verdade[i] = k

        for porta in self.portas:
            porta.roda_porta_tabela_verdade(tabela_verdade)

        return tabela_verdade

    def obtem_portas_string(self):
        s = [str(porta) for porta in self.portas]
        return s

    def salva_em_arquivo(self, nome_do_arquivo=None):
        conteudo = str(self)

        if nome_do_arquivo is None:
            timestamp = time.time()
            nome_do_arquivo = Path(f'./data/circuitos/{timestamp}_GC-{self.gc}_QC-{self.qc}.tfc')

        # safety-check
        arquivo = Path(nome_do_arquivo)
        arquivo.parent.mkdir(parents=True, exist_ok=True)

        arquivo.write_text(conteudo)

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise Exception('Tipo Circuito somente pode ser concatenado com outro de mesmo tipo.')

        # portas_invertidas = other.portas[::-1]
        # novas_portas = self.portas + portas_invertidas
        novas_portas = self.portas + other.portas
        nova_qtd_vars = max(self.tamanho_circuito, other.tamanho_circuito)
        novos_ancillas = max(self.bits_extras, other.bits_extras)

        novo_circuito = Circuito(novas_portas, nova_qtd_vars, novos_ancillas)

        # linhas_usadas = novo_circuito.__obtem_quantidade_de_variaveis()
        # novo_circuito.bits_extras = linhas_usadas - nova_qtd_vars

        # linhas_usadas = novo_circuito.obtem_linhas_usadas()
        # if len(linhas_usadas) > 0:
        #    novo_circuito.bits_extras = 1 + max(linhas_usadas) - nova_qtd_vars

        return novo_circuito

    def __repr__(self):
        s = ''
        s += f'# GATE_COUNT = {self.gc} \t\t QUANTUM_COST = {self.qc} \t\t ANCILLAS = {self.bits_extras}\n'

        # k = ','.join([f'b{i}' for i in sorted(self.obtem_linhas_usadas())])
        k = ','.join([f'b{i}' for i in range(self.tamanho_circuito + self.bits_extras)])
        s += f'.v {k}\n'
        s += f'.i {k}\n'
        s += f'.o {k}\n'

        s += 'BEGIN\n'
        for porta in self.portas:
            s += str(porta)
            s += '\n'

        s += 'END'
        return s

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.tamanho_circuito != other.tamanho_circuito:
            return False

        if len(self.portas) != len(other.portas):
            return False

        if self.portas != other.portas:
            return False

        return True

    def __lt__(self, other):
        return self.tamanho_circuito < other.tamanho_circuito

    def __len__(self):
        return len(self.portas)

    def __iter__(self):
        for porta in self.portas:
            yield porta


def extrai_coluna_da_matriz(matriz, posicao):
    return [int(linha[posicao]) for linha in matriz]


def gera_circuito(expressao, alvo, ancillas, qtd_vars, prefixo='b'):
    if expressao.strip() == '':
        return Circuito(qtd_vars=qtd_vars, ancillas=ancillas)

    portas = extrai_portas(expressao, alvo)

    portas_circuito = list()
    for p in portas:
        porta_circuito = gera_porta_circuito(p, alvo, prefixo=prefixo)
        portas_circuito.append(porta_circuito)

    return Circuito(portas_circuito, qtd_vars, ancillas=ancillas)


def extrai_portas(expressao, alvo):
    # reduz espaços da expressão
    expressao = ' '.join(expressao.split())

    portas = list()

    if expressao == '1':
        # return [f'~b{alvo}']
        porta = ''
        portas.append(porta)
        return portas

    portas = expressao.split('^')
    portas = [porta.strip() for porta in portas]
    reduz_representacao_portas(portas)

    return portas


def reduz_representacao_portas(portas):
    identificador_de_not = '1'

    if identificador_de_not in portas:
        # qual a quantidade de negacoes na expressao?
        qtd = portas.count(identificador_de_not)

        # se for par, é só remover
        for _ in range(qtd):
            portas.remove(identificador_de_not)

        # caso seja impar, adiciona uma negacao na frente
        if qtd % 2 == 1:
            portas[0] = '~' + portas[0]

    # return portas


def gera_estados(n: int, alvos: List[int], prefixo: str = 'x'):
    """
    Gera a lista de estados referente ao circuito desejado.

    :param n: Indica a quantidade de linhas que o circuito possui.
    :param alvos: Indica as linhas que representam os alvos existentes.
    :param prefixo: Qual deve ser o prefixo dos estados gerados?
    :return: Uma lista de estados contendo todas as linhas que não são alvos.
    """
    estados = []

    for i in range(0, n + 0):
        estado = f'{prefixo}{i}'

        if i not in alvos:
            estados.append(estado)

    return estados


def processa_permutacao(g, n, estados, nivel=0, prefixo='x', alvo=0):
    return processa_permutacao_aux(g, n, estados, nivel, prefixo, alvo)

XOR = '⊕'
VAZIO = 'Ø'
AND = '.'

def substitui_simbolos(expressao):
    expressao = expressao.replace(AND, '&')
    expressao = expressao.replace(XOR, '^')
    expressao = expressao.replace(VAZIO, '')

    # inclui '~' das variaveis
    # expressao = 'b1 ^ 1' ==> '~b1'
    regex = r'[a-zA-Z]+[0-9]+\s+\^\s+1'
    variaveis = re.findall(regex, expressao)
    for s in variaveis:
        tt = s.replace(' ^ 1', '')
        tt = '~' + tt
        expressao = expressao.replace(s, tt)

    # sanitiza expressão
    expressao = ' ' + expressao.strip(' ') + ' '
    while '  ' in expressao:
        expressao = expressao.replace('  ', ' ')

    return expressao


def gera_string_binaria_equivalente(s, estados, n, gerar_negativos=False, alvo=0):
    variaveis = list()

    # gera uma representacao binaria do indice do espectro de reed muller
    r = f'{s:b}'.zfill(n)

    for j, x in enumerate(r):
        if x == '1':
            k = f'{estados[j]}'
            variaveis.append(k)
        elif gerar_negativos and x == '0':
            k = f'~{estados[j]}'
            variaveis.append(k)

    return variaveis


def transforma_saida_funcao(f):
    """
    In the S coding, the {0, 1} values corresponding to true and false minterms are
    respectively replaced by the {1, −1} values.
    """

    g = list()
    t = {0: 1, 1: -1}

    for i in f:
        e = t.get(i)

        if e:
            g.append(e)
        else:
            raise Exception("The function contains errors. The output must contain only 0's and 1's")

    return np.array(g, dtype=np.int8)


def gera_matriz_walsh_hadamard(n):
    """
    Walsh functions can be generated in a recursive way by using the Hadamard
    matrix (Hurst et al., 1985).

    Tw(0) = [1]
    Tw(n) = [ [Tw(n - 1), Tw(n - 1)], [Tw(n - 1), -Tw(n - 1)] ]
    """

    h0 = np.array([[1, 1], [1, -1]], dtype=np.int8)
    h = h0
    while len(h) < n:
        h = np.kron(h, h0)

    return h


def multiplica_matrizes(h, f):
    """
    add @measure to test performance on this function.

    Function Name       : multiplica_matrizes (with matmul)
    Elapsed time        :     0.0189 msecs
    Current memory usage:     0.0006 MB
    Peak                :     0.0009 MB

    Function Name       : multiplica_matrizes (with dot)
    Elapsed time        :     0.0285 msecs
    Current memory usage:     0.0015 MB
    Peak                :     0.0068 MB
    """

    s = np.matmul(h, f)
    return s


def aplica_funcao_s(coef):
    """
    000 --> 0 -->
    001 --> 1 --> x3
    010 --> 2 --> x2
    100 --> 3 --> x1
    ...
    111 --> 7 --> x1x2x3
    """

    coef = list(coef)
    n = int(log2(len(coef)))

    valor, pos = identifica_maior_magnitude(coef)
    r = f'{pos:b}'.zfill(n)

    negado = False
    if valor < 0:
        negado = True

    # [f'x{j+1}' if x == '1' else '' for j, x in enumerate('111')]

    linhas = list()
    for i in range(len(coef)):
        str_linha = f'{i:b}'.zfill(n)
        linha = list(str_linha)
        # logger.debug(f'antes == {linha=}', end='\t')

        for j, x in enumerate(r):
            if x == '1':
                if negado:
                    linha[j] = '0' if linha[j] == '1' else '1'

        # logger.debug(f'depois == {linha=}')
        linhas.append(linha)

    saida = list()
    for linha in linhas:
        t = list()

        for j, x in enumerate(r):
            if x == '1':
                k = int(linha[j])
                t.append(k)

        # logger.debug(f'T antes  > {t}')
        t = reduz_linha_xor(t)
        # logger.debug(f'T depois > {t}')
        saida.append(t)

    return saida


def reduz_linha_xor(lin):
    """
    x1 ^ x2 ==> x1 XOR x2
    """
    if len(lin) < 1:
        return 0
    ll = [str(x) for x in lin]
    tt = '^'.join(ll)
    res = eval(tt)
    return res


def executa_linha(f0, estados, nivel, alvo=0):
    f1 = transforma_saida_funcao(f0)
    # espacos = '   ' * nivel

    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.hadamard.html
    n = len(f0)
    wh = gera_matriz_walsh_hadamard(n)
    # logger.debug(f'WH = {wh}')

    s = multiplica_matrizes(wh, f1)

    fn = aplica_funcao_s(s)

    d = concordancia_de_funcoes(f0, fn)

    r0 = d.count(0)
    r1 = d.count(1)
    r = min(r0, r1) / len(fn)

    eq_d = gera_equacao_d(s, estados, alvo=alvo)
    # logger.debug(f'EQ = {eq_d}')

    return r, eq_d, d


def identifica_maior_magnitude(coeficiente_espectral):
    """
    We find coefficients with the largest magnitudes. In our example this condition is satisfied
    for the coefficient s1 = −6. Hence, f(x) = f(x3).

    Example: [2, −6, 2, 2, −2, −2, −2, −2]
    """

    magnitudes = coeficiente_espectral[:]
    magnitudes.sort(key=abs, reverse=True)

    maior_magnitude = magnitudes[0]
    posicao = coeficiente_espectral.index(maior_magnitude)

    return maior_magnitude, posicao



def gera_equacao_d(coef, estados, simbolo_xor='⊕', alvo=0):
    n = int(log2(len(coef)))
    coef = list(coef)
    variaveis = list()

    valor, pos = identifica_maior_magnitude(coef)
    eq = ''

    variaveis += gera_string_binaria_equivalente(pos, estados, n, gerar_negativos=False, alvo=alvo)

    if len(variaveis) > 0 and valor < 0:
        variaveis.append('1')

    if '1' in variaveis:
        variaveis2 = list()

        for v in variaveis:
            if v != '1':
                v = f'~{v}'
                variaveis2.append(v)

        variaveis = variaveis2

    eq += f' {simbolo_xor} '.join(variaveis)
    # eq += f' {simbolo_xor} '


    return eq.strip(f' {simbolo_xor} ')


def concordancia_de_funcoes(f1, f2):
    """
    Compute the function d(x) = f (x) ⊕ fs (x). The function d(x) indicates the number of
    agreements (disagreements) between f (x) and fs (x) at point x:

    d(x) = 1 for f(x) != fs(x).
    d(x) = 0 for f(x) == fs(x).
    """

    d = list()

    if len(f1) != len(f2):
        raise Exception("The function contains errors. Functions should have the same length.")

    for i in range(len(f1)):
        x1 = f1[i]
        x2 = f2[i]

        r = 1 if x1 != x2 else 0

        d.append(r)

    return d


def determina_quantidades_de_bits(d):
    return int(log2(len(d)))


def particiona_permutacao(dh, k=0, n=None):
    """
        Divide o DH particionando através do elemento fixo K.
    """
    if n is None:
        n = determina_quantidades_de_bits(dh)

    dh1 = list()
    dh2 = list()

    for i, h in enumerate(dh):
        r = f'{i:b}'.zfill(n)

        if r[k] == '0':
            dh1.append(h)
        else:
            dh2.append(h)

    return [dh1, dh2]


# n: quantidade de bits (inclui o alvo?) supomos que sim
def processa_permutacao_aux(g, n, estados, nivel=0, prefixo='x', alvo=0):
    # logger.debug(f'Entrando na recursão nível {nivel}')

    # se DH possui apenas 1, então termina (equação é igual a 1)
    if g.count(1) == len(g):
        # logger.debug(f'Encontrei uma G sem entrada nula')
        return f'1'

    # se DH está zerado, então termina (equação vazia)
    if [0] * len(g) == g:
        # logger.debug(f'Equação (zerada) == {g}')
        return f'{VAZIO}'

    if g.count(1) < 2:
        # logger.debug(f'Encontrei uma G com apenas uma entrada não nula')
        posicao = g.index(1)
        str_bin = gera_string_binaria_equivalente(posicao, estados, n, gerar_negativos=True, alvo=alvo)
        equacao = ' . '.join(str_bin)

        return equacao

    # se DH tem menos de dois elementos, então termina
    if len(g) < 2:
        # logger.debug(f'Equação (tam<2) == {g}')
        # return f'?'
        return f'1'

    metade_tamanho = len(g) // 2
    primeira_metade_g = g[0:metade_tamanho]
    segundo_metade_g = g[metade_tamanho:len(g)]
    if primeira_metade_g == segundo_metade_g:
        novos_estados = estados[:]
        del novos_estados[0]

        v = processa_permutacao_aux(g=primeira_metade_g, n=n - 1, estados=novos_estados, nivel=nivel + 1,
                                    prefixo=prefixo, alvo=alvo)

        return v

    espacos = '   ' * nivel
    _, eqd, dh = executa_linha(g, estados, nivel, alvo=alvo - nivel)

    # Equação total (ou final) --- resposta da recursão
    eqt = []

    # se a equação encontra neste nível da recursão é vazia, ou
    # se a equação é simplesmente igual a 1, dai retorna vazio
    # c.c. junta a equação encontrada neste nível com a equação anterior (encontrada nos niveis acima)
    if eqd == '' or eqd.strip() == '1':
        eqd = f'{VAZIO}'
    else:
        eqt.append(eqd)

    if dh.count(1) == 1:
        # logger.debug(f'\t\t\tDH:{dh}')

        # logger.debug(f'\t*\tfinal: {v0} &\t {v1}')
        idx = dh.index(1)
        valor_str = f'{idx:b}'.zfill(n)
        # logger.debug(f'IDX - valor str:{valor_str}')

        posicao = dh.index(1)
        str_bin = gera_string_binaria_equivalente(posicao, estados, n, gerar_negativos=True, alvo=alvo)
        eqd = ' . '.join(str_bin)

        eqt.append(eqd)

        eq = f' {XOR} '.join(eqt)
        return eq

    n -= 1

    ##### REMOVER DEPOIS
    eq1 = ''
    eq2 = ''
    #####

    # logger.debug(f'n:{n}')
    if dh != [0] * n:
        # se novo DH não está zerado, particiona
        g1, g2 = particiona_permutacao(dh, k=0)

        # logger.debug(f'{espacos}EQ_D{nivel} = {eqd}')
        # logger.debug(f'{espacos}FP{nivel} = {eqd}')
        # logger.debug(f'{espacos}Particionando F{nivel} = {dh} em F{nivel + 1} = {g1} e F{nivel + 1}\' = {g2}')

        # estados_temp = estados[:alvo] + estados[alvo+1:]
        estados_temp = estados[1:]
        # logger.debug(f'{L=} {i=} {Ltemp=}')

        ind = estados[0]

        # logger.debug(f'       tbl_vdd = {dh} \t\t qtd_1s = {dh.count(1)}')
        # logger.debug(f'       tbl_g1 = {g1} \t\t qtd_1s = {g1.count(1)}')
        # logger.debug(f'       tbl_g2 = {g2} \t\t qtd_1s = {g2.count(1)}')

        # antes o parâmetro era n-1
        v0 = processa_permutacao_aux(g1, n, estados_temp, nivel + 1, prefixo, alvo - nivel)
        # logger.debug(f'{"---" * nivel}expr_F{nivel + 1} = {v0}')

        # antes o parâmetro era n-1
        v1 = processa_permutacao_aux(g2, n, estados_temp, nivel + 1, prefixo, alvo - nivel)
        # logger.debug(f'{"---" * nivel}expr_F{nivel + 1}\'= {v1}')

        # logger.debug(f'n:{n}')

        # logger.debug(f'V0 = {v0}')
        # logger.debug(f'V1 = {v1}')

        if v0 == '1':
            eq1 = f' ~{ind} '
            eqt.append(eq1)

        elif v0 != f'{VAZIO}':
            eq1t = list()
            for variavel in v0.split(f'{XOR}'):
                variavel = variavel.strip()
                eq1t.append(f' ~{ind} . {variavel}')

            eq1 = f' {XOR} '.join(eq1t)
            # logger.debug(f'EQ1 ==> {eq1} :: EQ1T ==> {eq1t}')

            # eq1 = f' ~{ind} . ( ' + str(v0) + ' )'
            eqt.append(eq1)

        if v1 == '1':
            eq2 = f' {ind} '
            eqt.append(eq2)

        elif v1 != f'{VAZIO}':
            eq2t = list()
            for variavel in v1.split(f'{XOR}'):
                variavel = variavel.strip()
                eq2t.append(f' {ind} . {variavel}')

            eq2 = f' {XOR} '.join(eq2t)
            # logger.debug(f'EQ2 ==> {eq2} :: EQ2T ==> {eq2t}')

            # eq2 = f' {ind} . ( ' + str(v1) + ' )'
            eqt.append(eq2)

    # logger.debug(f'{eq1=}')
    # logger.debug(f'{eq2=}')
    # logger.debug(f'{eqt=}')

    eq = f' {XOR} '.join(eqt)
    # logger.debug(f'{espacos}FT{nivel} = {eq}')

    return eq


def executa_sintese(n, tabela_saida, prefixo='b'):
    # verifica se a quantidad de linhas da entrada difere da quantidade de linhas de saída
    # if len(tabela_entrada) != len(tabela_saida):
    if (2 ** n) != len(tabela_saida):
        raise Exception('Tabela de saída incogruente com a tabela de entrada.')

    # infere alguns dados a partir das tabelas de entrada e saída
    # n = len(tabela_entrada[0])

    # 2024-07-19: gambiarra?
    if isinstance(tabela_saida[0], int):
        tabela_saida = [[i] for i in tabela_saida]
        # tabela_saida = [tabela_saida]

    ancillas = len(tabela_saida[0])

    # extrai todas as funções possiveis, dada uma tabela de saída (considerando a entrada 000, 001, 010, ... 110, 111)
    ## F_i = a i-ésima saída da função original (diretamente da tabela de saída informada)
    ## FXOR_i = a i-ésima função F_i aplicando um XOR com o valor do alvo, ou seja, FXOR = F_i XOR i
    funcoes = list()
    for i in range(ancillas):
        # extrai primeiramente os valores da i-ésima coluna
        f = extrai_coluna_da_matriz(tabela_saida, i)
        # f_alvo = extrai_coluna_da_matriz(tabela_entrada, i)
        # fxor = gera_f1_xor(f, f_alvo)

        # salva a F encontrada
        funcoes.append(f)

    # gera o circuito de cada expressao reed-muller, para cada funcao encontrada no passo anterior
    circuitos = list()
    for i, fxor in enumerate(funcoes):
        # gera a lista de estados para uma determinada linha de alvo
        linha_de_alvo = [n + i]
        estados = gera_estados(n, linha_de_alvo, prefixo=prefixo)
        # gera a expressao
        expressao = processa_permutacao(fxor, n, estados, prefixo=prefixo, alvo=i)
        # limpa a expressao gerada: remove espacos desncessarios, parenteses, etc
        expressao_tratada = substitui_simbolos(expressao)
        expressao_tratada = expressao_tratada.replace('(', '').replace(')', '').strip()
        # gera um circuito equivalente a partir da expressao encontrada
        circuito = gera_circuito(expressao_tratada, alvo=linha_de_alvo, ancillas=ancillas, qtd_vars=n,
                                 prefixo=prefixo)
        circuitos.append(circuito)

    circuito_final = Circuito(qtd_vars=n, ancillas=ancillas)
    for c in circuitos:
        circuito_final = circuito_final + c

    # logger.debug(f'Circuito Final:\n{circuito_final}')
    # circuito_final.reduz_linhas()
    return circuito_final


def main():
    # Entrada Padrão (3 bits)
    # entrada = [
    #     [0, 0, 0],
    #     [0, 0, 1],
    #     [0, 1, 0],
    #     [0, 1, 1],
    #     [1, 0, 0],
    #     [1, 0, 1],
    #     [1, 1, 0],
    #     [1, 1, 1],
    # ]

    # Saida aleatória 01
    # saida = [
    #     [0, 1],
    #     [0, 0],
    #     [1, 1],
    #     [1, 0],
    #     [1, 1],
    #     [0, 0],
    #     [0, 1],
    #     [1, 0],
    # ]

    # https://iopscience.iop.org/article/10.1088/2058-9565/acaf9d/meta
    # saida = [
    #     [0, 1, 0],
    #     [1, 0, 0],
    #     [1, 0, 0],
    #     [0, 1, 0],
    #     [1, 1, 0],
    #     [1, 0, 0],
    #     [0, 0, 0],
    #     [0, 1, 1],
    # ]

    # https://www.researchgate.net/profile/Stefano-Mancuso-2/publication/320674387_Computers_from_Plants_We_Never_Made_Speculations/links/5abf6d8aa6fdcccda65ac970/Computers-from-Plants-We-Never-Made-Speculations.pdf#page=120
    # saida = [
    #     [1],
    #     [1],
    #     [1],
    #     [1],
    #     [0],
    #     [0],
    #     [0],
    #     [1],
    # ]

    saida = [
        [0],
        [1],
        [0],
        [1],
        [0],
        [1],
        [1],
        [0],
    ]
    circ = executa_sintese(n=3, tabela_saida=saida)
    print(circ.__repr__())
    return

if __name__ == "__main__":
    main()