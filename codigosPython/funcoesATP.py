# -*- coding: utf-8 -*-
"""
Funções auxilio TCC.

Ambiente: Windows 10, 64-bit

@autor: Pedro Henrique Nascimento Vieira, 2016
"""
import re
import numpy as np
import scipy as sp

def criarBase(base, novo):
    '''
    Copiar o arquivo base e "setar" todas as seções da linha de transmissão
    para seções de 10 km.
    '''
    f_n = open(novo, 'x')
    
    with open(base, 'r') as f:
        for linha in f:
            for n in range(1,11):
                pt = re.compile("lttcc_L"+str(n)+".lib")
                linha = re.sub(pt, "lttcc_L10.lib", linha)
            
            f_n.write(linha)
            
    f_n.flush()
    f_n.close()
    

def simular(arquivo):
    from subprocess import call
    '''Arquivo refere-se ao caminho no computador que ele se encontra 
    (junto com a extensão .atp).'''    

    comando = ('C:\\ATPdraw\\tpbig1 '+ arquivo + ' > ' + arquivo[:-4] + 'Res.lis')
    
    # envia comandos para o command prompt
    call("COPY C:\\ATPdraw\\STARTUP STARTUP", shell = True)
    call(comando, shell = True)
        
    
def extrairResultados(arq):
    '''Lê um arquivo .lis e extrai o output colocando em outro arquivo.'''    
    f_n = open(arq + "resultado.txt", 'x')
    f_v = open(arq, 'r')
    
    procurandoInicio = True
    n = 0
    
    # procurar inicio dos resultados no arquivo;
    # ler resultados até encontrar linha com "Suspended simulation"
    for linha in f_v:
        if procurandoInicio and "EMTP output variables follow." in linha:
            procurandoInicio = False
            
        elif not procurandoInicio:
            if 'Step' in linha and 'Time' in linha:
                # split depois join na string para sumir com os espaços extras
                f_n.write(" ".join( linha.split() ) + "\n")
                
            elif n > 6:
                if ("Suspended simulation" in linha) or ("Final time step" in linha):
                    break
                
                elif "switch" in linha:
                    pass
                
                else:
                    res = linha.split()
                    try:
                        res.remove("SPY:")
                    except ValueError:
                        pass
                    
                    f_n.write(" ".join( res ) + "\n")
        
            else:
                n += 1
            
    n = 0
    # pular as linhas de suspensão até encontrar o final
    for linha in f_v:
        if n > 6:
            if ("Suspended simulation" in linha):
                n = 0
                
            elif ("Final time step" in linha):
                break
            
            elif "switch" in linha:
                    pass
                
            else:
                res = linha.split()
                try:
                    res.remove("SPY:")
                except ValueError:
                    pass
                
                f_n.write(" ".join( res ) + "\n")
                
        else:
            n += 1
            
    n = 0    
    # pegar último resultado, uma linha única que vem depois do final
    for linha in f_v:
        if n > 0:
            res = linha.split()
            
            try:
                res.remove("SPY:")
            except ValueError:
                pass
            
            f_n.write(" ".join( res ) + "\n")
            break
        
        else:
            n += 1
    
    f_v.close()
    f_n.flush()
    f_n.close()
    
    
def lerResultados(arq, extraido = False):
    '''Lê um arquivo com os resultados extraídos e, com ele, cria um  data frame.'''    
    import pandas as pd
    
    if extraido:        
        df = pd.read_csv(arq, sep = " ")
    else:
        df =  pd.read_csv(arq + "resultado.txt", sep = " ")
        
    nomes = list(df)[:2]
    
    v = ['XL001', 'V']
    # identificar as colunas a partir do nome das barras.
    # não há garantia que o ATP colocará os valores na mesma ordem sempre.
    for nome in list(df)[2:5]:
        if nome == v[0] + 'A':
            nome = v[1] + 'A'
            
        elif nome == v[0] + 'B':
            nome = v[1] + 'B'
            
        elif nome == v[0] + 'C':
            nome = v[1] + 'C'
    
        else:
            raise ValueError("Identificação inesperada para a barra")
            
        nomes += [nome]
        
    i = ['XL001', 'I']          
    for nome in list(df)[5:8]:
        if nome == i[0] + 'A.1':
            nome = i[1] + 'A'
            
        elif nome == i[0] + 'B.1':
            nome = i[1] + 'B'
            
        elif nome == i[0] + 'C.1':
            nome = i[1] + 'C'
    
        else:
            raise ValueError("Identificação inesperada para a barra")
            
        nomes += [nome]
        
    df.columns = nomes
    
    return df
          
    
def definirBarras(km):
    '''Função auxiliar. Determina a barra à montante e à jusante do km
    especificado.'''
    ponto = km/100
    x = 0.10
    
    # determinar a porcentagem do ponto
    while ponto > x:
        x += 0.10        
    
    # dar nome às barras a partir da porcentagem
    if x < 0.80:
        barra1 = "XL00" + str( round(x * 10) )
        barra2 = "XL00" + str( round((x + 0.10) * 10) )
        
    elif x < 0.9:
        barra1 = "XL009"
        barra2 = "XL010"
        
    else:
        barra1 = "XL010"
        barra2 = "XL011"
    
    return barra1, barra2
    
    
def definirSecoes(km):
    '''Função auxiliar. Determina o comprimento da primeira e segunda seção no
    qual dividir uma seção de 10 km.'''
    secao1 = km
    
    # extrai a unidade de 'km' de forma a ter uma seção menor que 10 km
    while secao1 > 10:
        # se o 'km' for grande, este loop pode demorar muito
        # considerar o uso de regex...
        secao1 -= 10
   
    secao2 = int(10 - secao1)
    secao1 = int(secao1)
    
    return secao1, secao2
    

def mudarResistenciaFalta(linhaTexto, fase, Rnovo, Rvelho = 0.5):
    '''Função auxiliar, muda o valor do resistor de falta.'''
    dicionario = {'A':'1', 'B':'2', 'C':'3'}   
    
    if ("XF000" + dicionario.get(fase)) in linhaTexto and ("XSWT0"  + 
                                        dicionario.get(fase)) not in linhaTexto:
        return re.sub(".5", str( float(Rnovo) ), linhaTexto)
    else:
        return linhaTexto
        

def replicarMudarResistencia(R, fase, titulo,
                     base = "C:\\ATPdraw\\ATP\\TCC\\Base\\cktBase.atp"):   
    '''
    Cria um arquivo novo, mudando a resistência de falta das fases especificadas,
    baseado em um arquivo pré-existente.
    
    Fases é uma string com o nome das fases (ABC) pra colocar a falta; a ordem
    não importa.
    '''
    
    nomeNovo = "C:\\ATPdraw\\ATP\\TCC\\" + titulo + ".atp"        
    novo = open(nomeNovo, 'x')
    velho = open(base, 'r')
    
    for linha in velho:
        lin = mudarResistenciaFalta(linha, R, fase)        
        novo.write(lin)
        
        
    novo.flush()
    novo.close()
     
     
def inserirFaltaFaseTerra(linhasTexto, barra1, barra2, secao1, secao2,
                          faseA, faseB, faseC):
    '''Função auxiliar. Substitui o nome das barras de forma a fazer a falta 
    fase terra.'''
    lin1 = ''
    lin2 = ''
    
    dicionario = {'A':'1', 'B':'2', 'C':'3'}
    
    # função auxiliar para trocar o nome das barras das linhas de texto
    def foo(substituir, fase, linha1, linha2):        
        z = dicionario.get(fase)
        
        if substituir:
            linha1 = re.sub(barra2 + fase, "XSWT0" + z, linha1)
            linha2 = re.sub(barra1 + fase, "XSWT0" + z, linha2)
        else:
            linha1 = re.sub(barra2 + fase, "XLINT" + fase, linha1)
            linha2 = re.sub(barra1 + fase, "XLINT" + fase, linha2)
        
        return linha1, linha2
        
    
    repl1 = "lttcc_L" + str(secao1) + ".lib"
    repl2 = "lttcc_L" + str(secao2) + ".lib"
    
    for l in linhasTexto:
        linha1 = re.sub("lttcc_L10.lib", repl1, l)
        linha2 = re.sub("lttcc_L10.lib", repl2, l)
                      
        linha1, linha2 = foo(faseA, "A", linha1, linha2)
        linha1, linha2 = foo(faseB, "B", linha1, linha2)        
        linha1, linha2 = foo(faseC, "C", linha1, linha2)
                    
        lin1 += linha1
        lin2 += linha2
        
    return lin1, lin2

    
def faltaFaseTerra10(km, titulo, fases = 'ABC',
                     base = "C:\\ATPdraw\\ATP\\TCC\\Base\\cktBase.atp"):
                         
    barra = definirBarras(km)[1]
    
    nomeNovo = "C:\\ATPdraw\\ATP\\TCC\\" + titulo + str(km) + ".atp"        
    novo = open(nomeNovo, 'x')
    
    with open(base) as arq:
        for linha in arq:
            if "XSWT0" in linha:                
                if 'A' in fases:
                    lin = re.sub("XSWT01", barra + 'A', linha)
                    
                elif 'B' in fases:
                    lin = re.sub("XSWT02", barra + 'B', linha)
                    
                elif 'C' in fases:
                    lin = re.sub("XSWT03", barra + 'C', linha)
                    
            else:
                lin = linha
                
            novo.write(lin)
            
    
    novo.flush()
    novo.close()
    
    

def replicarFaltaTerra(km, titulo, fases = 'ABC',
                     base = "C:\\ATPdraw\\ATP\\TCC\\Base\\cktBase.atp"):   
    '''
    Cria um arquivo novo com uma falta fase-terra com as fases especificadas,
    baseado em um arquivo pré-existente.
    
    Fases é uma string com o nome das fases (ABC) pra colocar a falta; a ordem
    não importa.
    '''
    if km % 10 == 0:
        return faltaFaseTerra10(km, titulo, fases = 'ABC',
                     base = "C:\\ATPdraw\\ATP\\TCC\\Base\\cktBase.atp")
        
    barra1, barra2 = definirBarras(km)
    
    secao1, secao2 = definirSecoes(km)
      
    def faltaNaFase(f):
        if f in fases:
            return True
        else:
            return False

    falta = [None, None, None]    
    t = 0
    
    for f in 'ABC':
        falta[t] = faltaNaFase(f)
        t+=1
    
    with open(base, 'r') as arq:
        # possível leak de memoria se o arquivo for grande
        todasLinhas = arq.readlines()

    nomeNovo = "C:\\ATPdraw\\ATP\\TCC\\" + titulo + str(km) + ".atp"        
    novo = open(nomeNovo, 'x')
    
    pular = False
    
    for n in range( len(todasLinhas) ):
        linha = todasLinhas[n]
        
        if pular:
            # pula essa linha de texto
            pular = False
        
        elif ("$INCLUDE" in linha) and (barra1 in linha) and (barra2 in linha):
            
            linhasTexto = todasLinhas[n : n+2]
            
            # cria duas linhas de texto para inserir no arquivo novo            
            lin1, lin2 = inserirFaltaFaseTerra(linhasTexto, barra1, barra2,
                                secao1, secao2, falta[0], falta[1], falta[2])
                                            
            pular = True
            
            novo.write(lin1)
            novo.write(lin2)
        
        else:
            novo.write(linha)
        
        
    novo.flush()
    novo.close()
    
    
def replicar99(titulo, fases = 'ABC',
                     base = "C:\\ATPdraw\\ATP\\TCC\\Base\\cktBase.atp"):
                         
    '''
    Cria falta fase-terra em todos os pontos (1 a 99) da linha usando o arquivo
    base especificado.
    '''    
    for km in range(1,100):
        replicarFaltaTerra(km, titulo, fases, base)
        

def amostrarMedidor(dados, taxaAmostragem = 500, periodoDados = 1e-6):
    '''
    
    Simula um medidor digital extraindo valores de dados de entrada.
    
    -------------
    Parâmetros:
        dados, dataframe de dados do qual extrair os valores, considerando
    que tenha um período igualmente espaçado entre valores;
        periodoDados = 1e-6, em segundos;
        taxaAmostragem = 500, em Hz
        
    Se (1/periodoDados/taxaAmostragem) não resultar em um valor inteiro,
    arredondamento é feito; pode levar a erros.
        
    -----------
    Retorna: 
        os valores capturados pelo medidor
    '''
    valoresAmostrados = dados.loc[dados['Step'] == 1]
    intervalo = round(1/periodoDados/taxaAmostragem)
    n = 0
    
    for valor in dados.Step:
        if n == intervalo:
            n = 1
            valoresAmostrados = valoresAmostrados.append(
                                            dados.loc[dados['Step'] == valor])
                        
        else:
            n += 1
            
    return valoresAmostrados


def pasta(f): return "C:\\ATPdraw\\ATP\\TCC\\FFT" + f + "0.5"

def arquivo(f, km): return pasta(f) + "\\FFT" + f + str(km) + "Res.lis"

def arquivoResultado(f, km): return arquivo(f, km) + "resultado.txt"

combinacoesFases = ['ABC', 'AB', 'AC', 'BC', 'A', 'B', 'C']

def extrairTodos():
    for fase in combinacoesFases:
            for km in range(1,100):
                extrairResultados(arquivo(fase, km))

def lerTodosArquivos(extraidos = True):
    '''apos arquivos organizados manualmente;'''    
    if not extraidos: #para não re-extrair
        extrairTodos()
    
    dados = {}
    for fase in combinacoesFases:
        for km in range(1,100):
            dados.update({"FFT" + fase + str(km) : lerResultados(
                                                arquivoResultado(fase, km), True)})
            
    return dados
    
        
def lerTodosArquivosFourier(extraidos=True):
    if not extraidos: #para não re-extrair
        extrairTodos()
        
    medidas = ['VA', 'VB', 'VC', 'IA', 'IB', 'IC']
    dados = {}
    for fase in combinacoesFases:
        for km in range(1,100):
            valores = lerResultados(arquivoResultado(fase, km), True)
            valores = amostrarMedidor(valores)
            valoresFourier = np.array([])
            for v in medidas:
                valoresFourier = np.hstack((valoresFourier, sp.fft(valores.get(v))))
                
            dados.update({"FFT" + fase + str(km) : valoresFourier})
            
    return dados #va,vb,vc,ia,ib,ic