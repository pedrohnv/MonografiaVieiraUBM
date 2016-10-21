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

############ Regressor
arrayPontos = np.array([])
for s in arrayKeys: #extrair o ponto da falta
    arrayPontos = np.append(arrayPontos, float(re.findall('\d+', s)[0]))
    

#random.seed(234947238) # Reserva 15.44 % para teste; gera um score de ~94 %
#random.seed(544628) # Reserva 13.56 % para teste; gera um score de ~87 %
random.seed(444) # Reserva 12.41 % para teste; gera um score de ~66 %

amostrasTreino = np.array([])
pontosTreino = np.array([])
amostrasTeste = np.array([])
pontosTeste = np.array([])

a = 0
for n in range(arrayPontos.size):
    if random.gauss(1.05, 1) > 0:
        try:
            amostrasTreino = np.vstack((amostrasTreino, valoresPadronizados[n]))
        except ValueError:
            amostrasTreino = valoresPadronizados[n]

        pontosTreino = np.append(pontosTreino, arrayPontos[n])
        
    else:
        a += 1
        try:
            amostrasTeste = np.vstack((amostrasTeste, valoresPadronizados[n]))
        except ValueError:
            amostrasTeste = valoresPadronizados[n]

        pontosTeste = np.append(pontosTeste, arrayPontos[n])
        
        
print("Dados reservados para Teste:", a/arrayPontos.size*100, "%")
    
cerebroRegressor = MLPRegressor(activation='logistic', max_iter=5000)
cerebroRegressor.fit(amostrasTreino, pontosTreino)

score = cerebroRegressor.score(amostrasTeste, pontosTeste)
print("Acertos:", score, "%")

# residuals teste
previstos = np.array([])
corretos = np.array([])
for n in range(amostrasTeste.shape[0]):
    previstos = np.append(previstos,
                          cerebroRegressor.predict(amostrasTeste[n]))
    
    corretos = np.append(corretos, pontosTeste[n])
    
plt.stem(corretos, previstos-corretos)
plt.ylabel("Erro (km)")
plt.xlabel("Ponto correto da falta (km)")
plt.title("Resíduos dos dados de teste, score: " + str(score))
plt.show()

print("Média:", np.abs(previstos-corretos).mean())
print("Desvio Padrão:", np.abs(previstos-corretos).std())
print("Mediana:", np.median(np.abs(previstos-corretos)))
print("Máximo:", np.abs(previstos-corretos).max())
print("Mínimo:", np.abs(previstos-corretos).min())
