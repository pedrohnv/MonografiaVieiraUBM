# -*- coding: utf-8 -*-
"""    
Código para criar as matrizes da representação em espaço de estado para
linhas de transmissão com efeito da frequência incluído como demonstrado em:
    
    KUROKAWA, S.; YAMANAKA, F. N. R.; PRADO, A. J.; BOVOLATO, L. F.; PISSOLATO, J. 
    Representação de linhas de transmissão por meio de variáveis de estado levando 
    em consideração o efeito da frequência sobre os parâmetros longitudinais. 
    Sba Controle & Automação, Campinas v.18, n.3, 2007, p.337-346, 2007.
    
O espaço de estado tem forma: [X'] = [A] * [X] + [B] * TensaoNoEmissor
    
Os atributos da Linha de Transmissão são:
    número de circuitos pi em cascata;
    
    condutância shunt de cada pi (S);
        total, não dividir por 2
        
    capacitância shunt de cada pi (F);
        total, não dividir por 2
        
    resistência série de cada pi (Ohm);
        R0, R1, R2, ..., Rm

    indutância série de cada pi (H);
        L0, L1, L2, ..., Lm

   
@author: Pedro Henrique Nascimento Vieira
"""
import numpy as np
import scipy as sp
        
class LinhaDeTransmissaoPiCascata(object):
    '''
    
    Classe que define uma linha de transmissão com uma fonte conectada no
    terminal emissor, e terminal receptor em vazio.
    '''
  
    def __init__(self, numeroCircuitoPi, comprimentoDaLinha, 
                 condutanciaDistribuida, capacitanciaDistribuida,
                 resistenciaDistribuida, indutanciaDistribuida):
    
        '''
        
        Construtor principal da classe. Define os atributos concentrados da linha,
        tendo como entrada os parâmetros distribuídos, o comprimento da linha e 
        o número de circuitos pi em cascata desejado.
        '''
        
        if not float(numeroCircuitoPi).is_integer():
            raise TypeError('numeroCircuitoPi deve ser um valor inteiro.')
        
        if numeroCircuitoPi <= 0:
            raise ValueError('numeroCircuitoPi deve ser maior que zero.')
            
        if resistenciaDistribuida.size != indutanciaDistribuida.size:
            raise ValueError('resistenciaDistribuida e indutanciaDistribuida ' +
                'devem ter o mesmo número de elementos.')
                     
        # ordem da linha, dimensão do espaço de estados gerado por ela
        self.ordem = (resistenciaDistribuida.size + 1) * numeroCircuitoPi
       
        # quantidade de circuitos pi em cascata representando a linha
        self.numeroCircuitoPi = int(numeroCircuitoPi)

        # comprimento de cada circuito pi, em km
        self.comprimentoSecaoPi = comprimentoDaLinha/numeroCircuitoPi

        # condutância shunt concentrada, em S
        self.condutanciaConcentrada = (condutanciaDistribuida * 
                                       self.comprimentoSecaoPi)

        # capacitância shunt concentrada, em F
        self.capacitanciaConcentrada = (capacitanciaDistribuida * 
                                        self.comprimentoSecaoPi)

        # resistência série concentrada, em Ohm
        self.resistenciaConcentrada = (np.array(resistenciaDistribuida) *
                                       self.comprimentoSecaoPi)
        
        # indutância série concentrada, em L
        self.indutanciaConcentrada = (np.array(indutanciaDistribuida) *
                                      self.comprimentoSecaoPi)
        

    def matrizTridiagonal(Ad, As, Ai, ordem):        
        if ordem == 1:
            return Ad
        
        valores = Ad.data
        linhas = Ad.row
        colunas = Ad.col
        
        m1 = Ad.shape[0]
                
        # diagonal principal
        for n in range(1, ordem):
            valores = np.append(valores, Ad.data)
            off = n * m1
            linhas = np.append(linhas, Ad.row + off)
            colunas = np.append(colunas, Ad.col + off)
            
        # diagonl superior
        for n in range(1, ordem):
            valores = np.append(valores, As.data)
            
            off1 = (n-1) * m1          
            off2 = n * m1
            
            linhas = np.append(linhas, As.row + off1)        
            colunas = np.append(colunas, As.col + off2)
            
        # diagonal inferior
        for n in range(1, ordem):
            valores = np.append(valores, Ai.data)
            
            off1 = n * m1
            off2 = (n-1) * m1
            
            linhas = np.append(linhas, Ai.row + off1)
            colunas = np.append(colunas, Ai.col + off2)
            
            
        return sp.sparse.coo_matrix((valores, (linhas, colunas)), 
                                shape = (ordem*m1, ordem*m1))
    
    
    def resolverSistemaEDO(A, B, u, t, x0 = None):
        '''        
        Resolve um sistema da forma: X'(t) = A*X(t) + B*u(t)
    
        Argumentos:
        -------
        A: uma matriz quadrada esparsa de ordem n
    
        B: um vetor esparso de dimensão n
    
        u: a entrada, uma função com argumento 't'
    
        t: os pontos nos quais x é calculado
    
        x0: as condições iniciais, nulas por padrão; dimensão n
    
        Retorna:
        --------
        X = um array da forma (len(t), len(x)) com os valores das variáveis
        calculados (resposta).
        '''
        if x0 == None:
            x0 = np.zeros(A.shape[0])
    
        if sp.sparse.issparse(A): A = A.tocsr()
            
        if sp.sparse.issparse(B): B = B.tocsr()
    
        def Bu(t):
            return B * u(t)
    
        def func(x, t): # dx/dt = f(x,t)
            # calcula a derivada das variáveis
            return (A * np.matrix(x).T + Bu(t)).A1
    
        return sp.integrate.odeint(func, x0, t)
    
        
    def espacoEstadosUmPi(self):
        '''
        
        Gera o espaço de estado de um circuito Pi.
        
        Parâmetros:
        -----
        Vin: tensão de entrada
        
        
        Retorna:
        ----
        [A, B]: matrizes esparsas no formato COOrdinate.
        dimensao da matriz A
        '''        
        # Matriz A
        # Os elementos não nulos são: primeira linha, primeira coluna, e
        # diagonal principal
        
        # elemento a_11 de A
        a_11 = -self.resistenciaConcentrada.sum() / self.indutanciaConcentrada[0]
        
        resistencias = self.resistenciaConcentrada[1:].copy()
        
        m = resistencias.size
        
        resistenciasPrimeiraLinha = resistencias / self.indutanciaConcentrada[0]
        
        resistencias = resistencias / self.indutanciaConcentrada[1:]
            
        # determinar a primeira linha, sem o primeiro elemento
        __lo = (-1) / self.indutanciaConcentrada[0]
        primeiraLinha = np.append(resistenciasPrimeiraLinha, __lo)
        
        # determinar a diagonal principal
        __gc = -self.capacitanciaConcentrada / self.condutanciaConcentrada
        diagonalPrincipal = np.append(a_11, -resistencias)
        diagonalPrincipal = np.append(diagonalPrincipal, __gc)

        # determinar a primeira coluna, sem o primeiro elemento
        __c2 = 2 / self.capacitanciaConcentrada
        primeiraColuna = np.append(resistencias, __c2)
        
        
        # A será criada como uma matriz esparsa. Os valores não nulos serão
        # entrados na ordem: diagonalPrincipal, primeiraColuna, primeiraLinha
        
        valoresA = np.append(diagonalPrincipal, primeiraColuna)
        valoresA = np.append(valoresA, primeiraLinha)
        
        indiceLinhas = [None] * valoresA.size
        indiceColunas = [None] * valoresA.size
        
        __s = diagonalPrincipal.size
        
        for n in range(__s): 
            indiceLinhas[n] = n
            indiceColunas[n] = n
        
        
        for n in range(primeiraColuna.size): 
            indiceLinhas[n + __s] = n + 1
            indiceColunas[n + __s] = 0
            
        
        __s += primeiraColuna.size
        
        for n in range(primeiraLinha.size): 
            indiceLinhas[n + __s] = 0
            indiceColunas[n + __s] = n + 1
            
            
        dimensao = m+2
        
        A = sp.sparse.coo_matrix((valoresA, (indiceLinhas, indiceColunas)),
                              shape = (dimensao, dimensao))
        
        valorB = np.array([-primeiraLinha[-1]]) # pega o último elemento
        
        B = sp.sparse.coo_matrix((valorB , ([0], [0])), shape = (dimensao, 1))
        
        return A,B

        
    def espacoEstadosLinha(self):
        '''
        
        Gera as matrizes do espaço de estados da linha
        '''
        M = self.espacoEstadosUmPi()
        
        # submatriz diagonal superior
        As = sp.sparse.coo_matrix( ([-1/self.capacitanciaConcentrada],
                                ([M[0].shape[0] - 1], [0])), shape = M[0].shape)
        
        # submatriz diagonal inferior
        Ai = sp.sparse.coo_matrix( ([1/self.indutanciaConcentrada[0]],
                                 ([0], [M[0].shape[0] - 1])), shape = M[0].shape)
        
        ordem = self.numeroCircuitoPi
        
        A = self.matrizTridiagonal(Ad=M[0], As=As, Ai=Ai, ordem=ordem)
        
        B = sp.sparse.coo_matrix((M[1].data, (M[1].row, M[1].col)), 
                                 shape = (A.shape[0], 1))
                
        return A, B
        
        
    def simularLinha(self, tensaoEmissor, t, x0 = None):
        '''
        
        Simula a linha considerando o terminal receptor em vazio.
        
        Argumentos:
        -------
        tensaoEmissor: a tensão no terminal emissor, uma função com argumento 't'
        
        t: os pontos nos quais X é calculado
        
        x0: as condições iniciais, nulas por padrão
        
        Retorna:
        --------
        um array da forma (len(t), len(x)) com os valores das variáveis calculados
        '''
        M = self.espacoEstadosLinha()
        
        return self.resolverSistemaEDO(M[0], M[1], tensaoEmissor, t, x0)