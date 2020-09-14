from numpy import linalg, array, matmul
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

#vê qual o numero máximo de nós para montar as matrizes
def conta_nos(lista):
    maximo = 0
    for i in range(len(lista)):
        if(int(lista[i][NO_INICIAL]) > maximo):
            maximo = int(lista[i][NO_INICIAL])
        if(int(lista[i][NO_FINAL]) > maximo):
            maximo = int(lista[i][NO_FINAL])
    return maximo

def cria_matriz(linhas, colunas):
    matriz = []
    for i in range(linhas):
        linha = []
        for i in range(colunas):
            linha.append(0)
        matriz.append(linha)
    return matriz

#trata casos de valores como por exemplo "1k, 500m"
def multiplica(valor):
    if (valor[-1] in multiplicadores):
        return float(valor[:-1]) * multiplicadores[valor[-1]]
    else:
        return valor


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

dimensao = conta_nos(netlist)
omega = 0
mat_G = cria_matriz(dimensao+1,dimensao+1) #adiciona-se 1 para compensar a linha e a coluna 0 serem excluídas
mat_i = cria_matriz(dimensao+1,1)
for i in range(len(netlist)):
    if netlist[i][-1][-1] == '\n':          #retira o '\n' do final das linhas para evitar erros de leitura
        netlist[i][-1] = netlist[i][-1][:-1]

    dis = netlist[i][DISPOSITIVO]
    origem = int(netlist[i][NO_INICIAL])
    destino = int(netlist[i][NO_FINAL])
    #identificação do tipo de dispostivo e o adiciona às matrizes de acordo com sua estampa
    if (dis[0] == 'R'):
        netlist[i][resistor["resistencia"]] = float(multiplica(netlist[i][resistor["resistencia"]]))
        mat_G[origem][origem] += 1/float(netlist[i][resistor["resistencia"]])
        mat_G[origem][destino] += -1/float(netlist[i][resistor["resistencia"]])
        mat_G[destino][origem] += -1/float(netlist[i][resistor["resistencia"]])
        mat_G[destino][destino] += 1/float(netlist[i][resistor["resistencia"]])
    if (dis[0] == 'I'):
        if re.search("^SIN", netlist[i][iS["corrente"]]):
            omega = str(netlist[i][-1][:-1]) #retira o ')' do final do valor da frequencia
            omega = 2*pi*float(multiplica(omega)) #toma a frequencia em radianos
            netlist[i][iS["corrente"]] = netlist[i][4]
        netlist[i][iS["corrente"]] = multiplica(netlist[i][iS["corrente"]])
        mat_i[origem][0] += -float(netlist[i][iS["corrente"]])
        mat_i[destino][0] += float(netlist[i][iS["corrente"]])
    if(dis[0] == 'G'):
        referenciaPos = int(netlist[i][REFP])
        referenciaNeg = int(netlist[i][REFN])
        mat_G[origem][referenciaPos] += float(netlist[i][icDC["transc"]])
        mat_G[origem][referenciaNeg] += -float(netlist[i][icDC["transc"]])
        mat_G[destino][referenciaPos] += -float(netlist[i][icDC["transc"]])
        mat_G[destino][referenciaNeg] += float(netlist[i][icDC["transc"]])
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

#Converte as matrizes para arrays do numpy
#e exclui a linha e a coluna do nó GND (nó 0)
mat_G = array(mat_G)
mat_G = mat_G[1:,1:]
mat_i = array(mat_i)
mat_i = mat_i[1:,0]

resultado =  matmul(linalg.inv(mat_G), mat_i)
print("Resultados---------------------------------------")
if(omega == 0):
    for i in range(len(resultado)):
        print(f'V({i+1}): {round(resultado[i],4)} V')
else:
    for i in range(len(resultado)):
        print(f'V({i+1}): {round(resultado[i].real,3)}sin({round(omega,3)}t) + {round(resultado[i].imag,3)}cos({round(omega,3)}t) V')
