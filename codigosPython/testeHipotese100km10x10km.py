# -*- coding: utf-8 -*-
"""
Codigo para testar a HIPÓTESE: UMA SEÇÃO DE 100 KM GERARÁ OS MESMOS RESULTADOS
QUE 10 SEÇÕES DE 10 KM.

Os resultados são lidos e comparados.

@autor: Pedro Henrique Nascimento Vieira, 2016
"""
import numpy as np
import funcoesATP as fatp
import matplotlib.pyplot as plt

try:
    fatp.criarBase(base = "C:\\ATPdraw\\ATP\\TCC\\Base\\prototipo.atp",
             novo = "C:\\ATPdraw\\ATP\\TCC\\Base\\cktBase.atp")             
except FileExistsError:
    pass

fatp.simular("C:\\ATPdraw\\ATP\\TCC\\Base\\cktBase.atp")

valores = ["VA", "VB", "VC", "IA", "IB", "IC"]

def plotarValores(df1, df2, v, nome1 = 'df1', nome2 = 'df2', 
                  titulo = "resultados"):
    plt.plot(df1.Time, df1.get(v), '--')
    plt.plot(df2.Time, df2.get(v))
    plt.legend((nome1, nome2), bbox_to_anchor = (1.0, 0.25))
    plt.xlabel("Tempo (s)")
    plt.ylabel(v)
    plt.title(titulo)
    plt.xlim(df1.Time.min(), df1.Time.max())    
    plt.show()
    
   
## Análise da linha transposta

dezSecoesTransposta = "C:\\ATPdraw\\ATP\\TCC\\Base\\cktBaseRes.lis"
secaoUnicaTransposta = "C:\\ATPdraw\\ATP\\TCC\\Base\\TESTE_100KM_TRANSPOSTA.lis"

fatp.extrairResultados(dezSecoesTransposta)
fatp.extrairResultados(secaoUnicaTransposta)

dfDezTransposta = fatp.lerResultados(dezSecoesTransposta)
dfUnicaTransposta = fatp.lerResultados(secaoUnicaTransposta)
    
for v in valores:
    titulo = v + ", Transposta"
    plotarValores(dfDezTransposta, dfUnicaTransposta, v, "Dez Seções", 
                  "Seção Única", titulo)
    
# fases parecem trocadas...
plt.plot(dfDezTransposta.Time, dfDezTransposta.get('VB'), '--')
plt.plot(dfUnicaTransposta.Time, dfUnicaTransposta.get('VA'))
plt.legend(("VB Dez Seções", "VA Seção Única"), bbox_to_anchor = (1.0, 0.25))
plt.xlabel("Tempo (s)")
plt.xlim(dfDezTransposta.Time.min(), dfDezTransposta.Time.max())    
plt.show()
    
plt.plot(dfDezTransposta.Time, dfDezTransposta.get('VC'), '--')
plt.plot(dfUnicaTransposta.Time, dfUnicaTransposta.get('VB'))
plt.legend(("VC Dez Seções", "VB Seção Única"), bbox_to_anchor = (1.0, 0.25))
plt.xlabel("Tempo (s)")
plt.xlim(dfDezTransposta.Time.min(), dfDezTransposta.Time.max())    
plt.show()
    
plt.plot(dfDezTransposta.Time, dfDezTransposta.get('VA'), '--')
plt.plot(dfUnicaTransposta.Time, dfUnicaTransposta.get('VC'))
plt.legend(("VA Dez Seções", "VC Seção Única"), bbox_to_anchor = (1.0, 0.25))
plt.xlabel("Tempo (s)")
plt.xlim(dfDezTransposta.Time.min(), dfDezTransposta.Time.max())    
plt.show()
    

## Análise da linha não transposta
unicaNaoTrans = "C:\\ATPdraw\\ATP\\TCC\\Base\\TESTE_100KM_NAO_TRANSPOSTA.lis"
dezNaoTrans = "C:\\ATPdraw\\ATP\\TCC\\Base\\TESTE_10_SECOES_NAO_TRANSPOSTA.lis"

fatp.extrairResultados(unicaNaoTrans)
fatp.extrairResultados(dezNaoTrans)

dfUnicaNaoTrans = fatp.lerResultados(unicaNaoTrans)
dfDezNaoTrans = fatp.lerResultados(dezNaoTrans)

for v in valores:
    titulo = v + ", não transposta"
    plotarValores(dfDezNaoTrans, dfUnicaNaoTrans, v, "Dez Seções", 
                  "Seção Única", titulo)


for v in valores:
    r = np.abs((dfDezNaoTrans.get(v) - dfUnicaNaoTrans.get(v)) / 
               dfUnicaNaoTrans.get(v))
    print("Erro relativo (%):", v)
    print(r.describe())
    print()
    
# caracterizar outliers
for v in valores:
    r = np.abs((dfDezNaoTrans.get(v) - dfUnicaNaoTrans.get(v)) /
               dfUnicaNaoTrans.get(v))
    n = 0    
    q = r.quantile(.999)
    for x in r:
        if x > q:
            n += 1
                
    print("% outliers de", v,":", n/r.size, "%")
    print("% outliers de", v,":", n/r.size, "%")
