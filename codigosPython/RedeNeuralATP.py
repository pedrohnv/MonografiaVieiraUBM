# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 10:55:39 2016

Codigo para treinar a rede neural com os resultados simulados no ATP.

@author: Pedro Henrique Nascimento Vieira, 2016
"""
import funcoesATP as fatp
import pandas as pd
import numpy as np
from sklearn.neural_network import MLPClassifier
import warnings
warnings.filterwarnings('ignore') # many deprecation warnings

# shape = (n_amostras, n_features)
dados = fatp.lerTodosArquivosFourier()

# formatar dados e padronizar valores para variância 1 e média 0
# valores reais são separados dos imaginários, e concatenados horizontalmente
# depois a normalização é feita
arrayKeys = []
for situacao in dados.keys():
    arrayKeys += [situacao]
    
    novosValores = np.hstack((dados.get(situacao).real, dados.get(situacao).imag))
    try:        
        arrayValores = np.vstack((arrayValores, novosValores))
    except NameError:
        arrayValores = np.array(novosValores)
        
valoresPadronizados = (arrayValores - arrayValores.mean())/arrayValores.std()

# rede neural classificadora
cerebro = MLPClassifier(activation='logistic', max_iter=10000)
cerebro.fit(valoresPadronizados, np.array(arrayKeys))

# testar valores e quantificar quantos erros e acertos
acertos = 0
resultadosErrados = {} #key: resultado previsto, valor: resultado correto
for n in range(valoresPadronizados.shape[0]):
    if cerebro.predict(valoresPadronizados[n]) == arrayKeys[n]:
        acertos += 1
    else:
        resultadosErrados.update({cerebro.predict(valoresPadronizados[n])[0] :
            arrayKeys[n]})
        
resultadosErrados = pd.DataFrame.from_dict(resultadosErrados, orient='index')
resultadosErrados.columns = ["previsto/correto"]

print("Total de acertos:", acertos)
print("Acertos:", acertos/valoresPadronizados.shape[0]*100, "%")
resultadosErrados
