from numpy import linalg, array, matmul, zeros, append
from sys import argv
from math import pi,sqrt
import string
import re

#definição de constantes
DISPOSITIVO = 0
NO_INICIAL = 1
NO_FINAL = 2
VALOR = 3
REFP = 3
REFN = 4
multiplicadores = {"n":0.000000001, "u":0.000001, "m":0.001, "k":1000, "Meg":1000000}
resistor = {"no+":1, "no-":2, "resistencia":3}
iS = {"noS": 1, "noE": 2, "corrente":3}
icDC = {"noS": 1, "noE": 2, "ref+":3, "ref-":4, "transc":5}

#vê qual o numero de nós e guarda seus nomes em um dicionário
def conta_nos(lista):
    numero_nos = 0
    nos = {'0':0}    #cria um dicionário já com o nó 0
    for i in range(len(lista)):
        if(lista[i][NO_INICIAL] not in nos):
            numero_nos += 1
            nos[lista[i][NO_INICIAL]] = numero_nos
        if(lista[i][NO_FINAL] not in nos):
            numero_nos += 1
            nos[lista[i][NO_FINAL]] = numero_nos
    return numero_nos, nos

#trata casos de valores como por exemplo "1k, 500m"
def multiplica(valor):
    if (valor[-1] in multiplicadores):
        return float(valor[:-1]) * multiplicadores[valor[-1]]
    else:
        return valor

#verifica se existe alguma fonte senoidal e guarda a frequência
def encontra_omega(lista):
    frequencia = 0
    for i in range(len(lista)):
        if re.search("^SIN", lista[i][iS["corrente"]]):
            if netlist[i][-1][-1] == '\n':          #retira o '\n' do final das linhas para evitar erros de leitura
                netlist[i][-1] = netlist[i][-1][:-1]
            frequencia = str(lista[i][-1][:-1]) #retira o ')' do final do valor da frequencia
            frequencia = 2*pi*float(multiplica(frequencia)) #toma a frequencia em radianos
    return frequencia

#abertura do arquivo com a netlist
file_name = str(argv[1])
arquivo_aberto = False
while not arquivo_aberto:
    # file_name = input("Digite o nome do arquivo a ser lido: ")
    try:
        file = open(file_name)
    except FileNotFoundError:
        file_name = input("Arquivo não encontrado!Digite novamente: ")
    else:
        arquivo_aberto = True

#leitura do arquivo e formatação das linhas
netlist = file.readlines()
file.close()
netlist  = [i.split(' ') for i in netlist]

dimensao, nomes_nos = conta_nos(netlist)
print(dimensao)
omega = encontra_omega(netlist)
mat_G = zeros((dimensao+1,dimensao+1),dtype=complex) #adiciona-se 1 para compensar a linha e a coluna 0 serem excluídas
mat_i = zeros((dimensao+1,1),dtype=complex)
for i in range(len(netlist)):
    if netlist[i][-1][-1] == '\n':          #retira o '\n' do final das linhas para evitar erros de leitura
        netlist[i][-1] = netlist[i][-1][:-1]
        
    dis = netlist[i][DISPOSITIVO]
    origem = nomes_nos[netlist[i][NO_INICIAL]] #retorna um número correspondente do nó
    destino = nomes_nos[netlist[i][NO_FINAL]]
    #identificação do tipo de dispostivo e o adiciona às matrizes de acordo com sua estampa
    if (dis[0] == 'R'):
        netlist[i][resistor["resistencia"]] = float(multiplica(netlist[i][resistor["resistencia"]]))
        mat_G[origem][origem] += 1/float(netlist[i][resistor["resistencia"]])
        mat_G[origem][destino] += -1/float(netlist[i][resistor["resistencia"]])
        mat_G[destino][origem] += -1/float(netlist[i][resistor["resistencia"]])
        mat_G[destino][destino] += 1/float(netlist[i][resistor["resistencia"]])
    if (dis[0] == 'I'):
        if re.search("^SIN", netlist[i][iS["corrente"]]):
            netlist[i][iS["corrente"]] = netlist[i][4]
        if re.search("^DC", netlist[i][iS["corrente"]]):
            netlist[i][iS["corrente"]] = netlist[i][4]
        netlist[i][iS["corrente"]] = multiplica(netlist[i][iS["corrente"]])
        mat_i[origem][0] += -float(netlist[i][iS["corrente"]])
        mat_i[destino][0] += float(netlist[i][iS["corrente"]])
    if(dis[0] == 'V'):
        if re.search("^SIN", netlist[i][iS["corrente"]]):
            netlist[i][iS["corrente"]] = netlist[i][4]
        if re.search("^DC", netlist[i][iS["corrente"]]):
            netlist[i][iS["corrente"]] = netlist[i][4]
        horizontal = zeros((1,dimensao+1))
        vertical = zeros((dimensao+2,1))
        dimensao +=1
        horizontal[0,origem] += -1
        horizontal[0,destino] += 1
        vertical[origem,0] += 1
        vertical[destino,0] += -1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i,array([[-float(multiplica(netlist[i][iS["corrente"]]))]]),axis=0)
    if(dis[0] == 'C'):
        mat_G[origem][origem] += float(multiplica(netlist[i][VALOR]))*1j*omega
        mat_G[origem][destino] += -float(multiplica(netlist[i][VALOR]))*1j*omega
        mat_G[destino][origem] += -float(multiplica(netlist[i][VALOR]))*1j*omega
        mat_G[destino][destino] += float(multiplica(netlist[i][VALOR]))*1j*omega
    if(dis[0] == 'L'):
        mat_G[origem][origem] += 1/(float(multiplica(netlist[i][VALOR]))*1j*omega)
        mat_G[origem][destino] += -1/(float(multiplica(netlist[i][VALOR]))*1j*omega)
        mat_G[destino][origem] += -1/(float(multiplica(netlist[i][VALOR]))*1j*omega)
        mat_G[destino][destino] += 1/(float(multiplica(netlist[i][VALOR]))*1j*omega)
    if(dis[0] == 'G'):
        referenciaPos = nomes_nos[netlist[i][REFP]]
        referenciaNeg = nomes_nos[netlist[i][REFN]]
        mat_G[origem][referenciaPos] += float(netlist[i][icDC["transc"]])
        mat_G[origem][referenciaNeg] += -float(netlist[i][icDC["transc"]])
        mat_G[destino][referenciaPos] += -float(netlist[i][icDC["transc"]])
        mat_G[destino][referenciaNeg] += float(netlist[i][icDC["transc"]])
    if(dis[0] == 'E'):
        referenciaPos = nomes_nos[netlist[i][REFP]]
        referenciaNeg = nomes_nos[netlist[i][REFN]]
        ganho = float(netlist[i][icDC["transc"]])
        horizontal = zeros((1,dimensao+1))
        vertical = zeros((dimensao+2,1))
        dimensao += 1
        horizontal[0,referenciaPos] += ganho
        horizontal[0,referenciaNeg] += -ganho
        horizontal[0,origem] += -1
        horizontal[0,destino] += 1
        vertical[origem,0] += 1
        vertical[destino,0] += -1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i,array([[0]]),axis=0)
    if(dis[0] == 'F'):
        referenciaPos = nomes_nos[netlist[i][REFP]]
        referenciaNeg = nomes_nos[netlist[i][REFN]]
        ganho = float(netlist[i][icDC["transc"]])
        horizontal = zeros((1,dimensao+1))
        vertical = zeros((dimensao+2,1))
        dimensao += 1
        vertical[referenciaPos,0] += 1
        vertical[referenciaNeg,0] += -1
        vertical[origem,0] += ganho
        vertical[destino,0] += -ganho
        horizontal[0,referenciaPos] += -1
        horizontal[0,referenciaNeg] += 1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i,array([[0]]),axis=0)
    if(dis[0] == 'H'):
        referenciaPos = nomes_nos[netlist[i][REFP]]
        referenciaNeg = nomes_nos[netlist[i][REFN]]
        ganho = float(netlist[i][icDC["transc"]])
        horizontal = zeros((1,dimensao+1))
        vertical = zeros((dimensao+2,1))
        dimensao += 1
        horizontal[0,referenciaPos] += -1
        horizontal[0,referenciaNeg] += 1
        vertical[referenciaPos,0] += 1
        vertical[referenciaNeg,0] += -1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i,array([[0]]),axis=0)
        horizontal = zeros((1,dimensao+1))
        vertical = zeros((dimensao+2,1))
        dimensao += 1
        horizontal[0,origem] += -1
        horizontal[0,destino] += 1
        horizontal[0,-1] += ganho
        vertical[origem,0] += 1
        vertical[destino,0] += -1
        mat_G = append(mat_G, horizontal, axis=0)
        mat_G = append(mat_G, vertical, axis=1)
        mat_i = append(mat_i,array([[0]]),axis=0)
        

#Converte as matrizes para arrays do numpy
#e exclui a linha e a coluna do nó GND (nó 0)
mat_G = mat_G[1:,1:]
mat_i = mat_i[1:,0]
del nomes_nos['0']

resultado =  matmul(linalg.inv(mat_G), mat_i)
print("Resultados---------------------------------------")
if(omega == 0):
    for i in nomes_nos:
        print(f'V({i}): {round(resultado[nomes_nos[i]-1].real,4)} V')
else:
    for i in nomes_nos:
        função = f'V({i}): {round(resultado[nomes_nos[i]-1].real,3)}sin({round(omega,3)}t)'
        if (resultado[nomes_nos[i]-1].imag != 0.0):
            função +=  f'+ {round(resultado[nomes_nos[i]-1].imag,3)}cos({round(omega,3)}t) V'
        print(função)