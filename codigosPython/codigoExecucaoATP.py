# -*- coding: utf-8 -*-
"""
Codigo procedual executado para fazer o TCC com o EMTP-ATP. Ele é
encarregado de criar e executar as simulações.

Ambiente: Windows 10, 64-bit

@autor: Pedro Henrique Nascimento Vieira, 2016
"""
import funcoesATP as fatp

# compilou-se (criou) o arquivo prototipo.atp, movidos para a pasta Base.
# a partir dele, criado o novo arquivo base
try:
    fatp.criarBase(base = "C:\\ATPdraw\\ATP\\TCC\\Base\\prototipo.atp",
             novo = "C:\\ATPdraw\\ATP\\TCC\\Base\\cktBase.atp")  

    fatp.simular("C:\\ATPdraw\\ATP\\TCC\\Base\\cktBase.atp")
    fatp.extrairResultados("C:\\ATPdraw\\ATP\\TCC\\Base\\cktBaseRes.lis")
except FileExistsError:
    pass

base = "C:\\ATPdraw\\ATP\\TCC\\Base\\cktBase.atp"

# gerar arquivos com falta fase terra.
fatp.replicar99("FFTA", fases = 'A', base = base)
# Simular cada um dos arquivos para cirar os arquivos .lis
for km in range(1,100):
    fatp.simular("C:\\ATPdraw\\ATP\\TCC\\FFTA" + str(km)+ ".atp")


# A cada simulação os arquivos foram movidos manualmente para pastas separadas    
fatp.replicar99("FFTB", fases = 'B', base = base)
for km in range(1,100):
    fatp.simular("C:\\ATPdraw\\ATP\\TCC\\FFTB" + str(km)+ ".atp")


fatp.replicar99("FFTC", fases = 'C', base = base)
for km in range(1,100):
    fatp.simular("C:\\ATPdraw\\ATP\\TCC\\FFTC" + str(km)+ ".atp")


fatp.replicar99("FFTAB", fases = 'AB', base = base)
for km in range(1,100):
    fatp.simular("C:\\ATPdraw\\ATP\\TCC\\FFTAB" + str(km)+ ".atp")
    
    
fatp.replicar99("FFTAC", fases = 'AC', base = base)
for km in range(1,100):
    fatp.simular("C:\\ATPdraw\\ATP\\TCC\\FFTAC" + str(km)+ ".atp")
    

fatp.replicar99("FFTBC", fases = 'BC', base = base)
for km in range(1,100):
    fatp.simular("C:\\ATPdraw\\ATP\\TCC\\FFTBC" + str(km)+ ".atp")
    
    
fatp.replicar99("FFTABC", fases = 'ABC', base = base)
for km in range(1,100):
    fatp.simular("C:\\ATPdraw\\ATP\\TCC\\FFTABC" + str(km)+ ".atp")
    
    
    