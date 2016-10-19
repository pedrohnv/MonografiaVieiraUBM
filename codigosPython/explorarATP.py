# -*- coding: utf-8 -*-
"""
Codigo para explorar o resultado das simulações do EMTP-ATP.

Ambiente: Windows 10, 64-bit

@autor: Pedro Henrique Nascimento Vieira, 2016
"""
import funcoesATP as fatp
import scipy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d

# apos arquivos organizados manualmente; extrair resultados:
dados = fatp.lerTodosArquivos()

arqBase = "C:\\ATPdraw\\ATP\\TCC\\Base\\cktBaseRes.lisresultado.txt"
cktbase = fatp.lerResultados(arqBase, True)
sinalNormal = fatp.amostrarMedidor(cktbase, 2000)

numAmostras = sinalNormal.shape[0]
# frequencia de amostragem, Hz
fs = 1/(np.array(sinalNormal.Time)[1] - np.array(sinalNormal.Time)[0])

numTransitorio = int(numAmostras/2)
sinalNormalDuranteTransitorio = sinalNormal[numTransitorio:]
n = sinalNormalDuranteTransitorio.Step.size

k = np.arange(n)
T = n/fs
frq = k/T # two sides frequency range
frq = frq[range(int(n/2))] # range de frequências

def plotarFourier3D(fase, medida):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for km in range(1,100):
        medidor = fatp.amostrarMedidor(dados.get("FFT" + fase + str(km)), fs)
        sinal = medidor.get(medida)
        
        sinal = sinal[numTransitorio:] # so o transitorio
        sinalFFT = sp.fft(sinal)/n # fft normalizada
        
        y = frq
        z = np.log10( abs(sinalFFT[range(int(n/2))]) + 1)
        x = np.ones(y.size) * km
        
        ax.plot(x,y,z)
    
    ax.set_ylabel('Freq (Hz)')
    ax.set_zlabel('log(|Y(freq)|)')
    ax.set_xlabel('dist (km)')
    plt.title('fase:' + fase + "; medida:" + medida)
    plt.show()

#plotar tudo; computacionalmente intenso, considere plotar um por vez
combinacoesFases = ['ABC', 'AB', 'AC', 'BC', 'A', 'B', 'C']
medidas = ['VA', 'VB', 'VC', 'IA', 'IB', 'IC']
if False: # mude para True para plotar tudo
    for fase in combinacoesFases:
        for m in medidas:
            plotarFourier3D(fase, m)
        
