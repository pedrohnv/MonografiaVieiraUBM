# -*- coding: utf-8 -*-
"""
Código para resolver o sistema de espaço de estado de linhas de transmissão 
com efeito da frequência incluído, como demonstrado em:

KUROKAWA, S.; YAMANAKA, F. N. R.; PRADO, A. J.; BOVOLATO, L. F.; PISSOLATO, J. 
Representação de linhas de transmissão por meio de variáveis de estado levando 
em consideração o efeito da frequência sobre os parâmetros longitudinais. 
Sba Controle & Automação, Campinas v.18, n.3, 2007, p.337-346, 2007.

As equações de estado tem forma: [X'(t)] = [A][X(t)] + [B]VE(t)

Considera-se condições iniciais nulas.

@author: Pedro Henrique Nascimento Vieira
"""
import numpy as np
from classeLinhaDeTransmissaoPiCascata import LinhaDeTransmissaoPiCascata
import matplotlib.pyplot as plt
from time import perf_counter

inicio = perf_counter()

def tensaoEmissor(t):
    return 20e3 # corrente-contínua, em V

dt = 5e-6 # passo de tempo, segundos
tFinal = 0.5e-3 # tempo final, sugere-se que seja um múltiplo inteiro de dt
t = np.arange(0, tFinal, dt)

numeroCircuitoPi = 30 # número de circuitos pi utilizados (= n)

comprimentoLinha = 10 # comprimento da linha em km

condutanciaDistribuida = 0.556e-6 # condutância distribuída (S/km)

capacitanciaDistribuida = 11.11e-9 # capacitância distribuída (F/km)

# Resistência distribuída (Ohm/km)
resistenciaDistribuida = np.array([0.026, 1.470, 2.354, 20.149, 111.111])

# Indutância distribuída (H/km)
indutanciaDistribuida = np.array([2.209, 0.740, 0.120, 0.100, 0.050]) * 1e-3

# inicializa um novo objeto da classe LinhaDeTransmissao
linhaTransmissao = LinhaDeTransmissaoPiCascata(numeroCircuitoPi, comprimentoLinha,
                            condutanciaDistribuida, capacitanciaDistribuida,
                            resistenciaDistribuida, indutanciaDistribuida)

M = linhaTransmissao.espacoEstadosLinha()

inicioInt = perf_counter()

y = linhaTransmissao.simularLinha(tensaoEmissor, t)

fimInt = perf_counter()

plt.plot(t, y[:, (y.shape[1]-1)])
plt.title('VE; dt = ' + str(dt))
plt.ylim((-10e3,45e3))
plt.show()

print("Integração demorou:", fimInt-inicioInt, "segundos")
print("Total:", perf_counter()-inicio, "segundos")

